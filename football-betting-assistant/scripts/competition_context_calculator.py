#!/usr/bin/env python3
"""Calculate group standings and qualification context from match results.

The script is intentionally source-agnostic. Public/API collectors can normalize
official standings or played results into this input shape, then this script
recomputes the table and motivation labels without depending on live services.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_WIN_POINTS = 3
DEFAULT_DRAW_POINTS = 1


@dataclass
class TeamRecord:
    team: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.wins * DEFAULT_WIN_POINTS + self.draws * DEFAULT_DRAW_POINTS

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def as_dict(self, rank: int, remaining_matches: int, advance_top_n: int, best_third_places: int) -> dict[str, Any]:
        return {
            "team": self.team,
            "rank": rank,
            "played": self.played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "points": self.points,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "remaining_matches": remaining_matches,
            "qualification_pressure": qualification_pressure(rank, remaining_matches, advance_top_n, best_third_places),
            "rotation_risk": rotation_risk(rank, remaining_matches, advance_top_n),
            "motivation_flags": motivation_flags(rank, remaining_matches, advance_top_n, best_third_places),
            "knockout_route_context": knockout_route_context(rank, advance_top_n, best_third_places),
        }


def qualification_pressure(rank: int, remaining_matches: int, advance_top_n: int, best_third_places: int) -> str:
    if remaining_matches <= 0:
        return "赛程已完结"
    if rank <= advance_top_n:
        return "直接晋级区，重点判断排名和轮换"
    if best_third_places and rank == advance_top_n + 1:
        return "第三名竞争区，仍需积分和净胜球"
    return "出线压力高，通常需要主动抢分"


def rotation_risk(rank: int, remaining_matches: int, advance_top_n: int) -> str:
    if remaining_matches <= 0:
        return "无"
    if rank <= advance_top_n:
        return "中：若排名压力低，可能控制节奏或轮换"
    return "低：通常仍需争取结果"


def motivation_flags(rank: int, remaining_matches: int, advance_top_n: int, best_third_places: int) -> list[str]:
    if remaining_matches <= 0:
        return ["completed"]
    flags: list[str] = []
    if rank <= advance_top_n:
        flags.extend(["already_in_advance_zone", "route_selection_risk"])
        if rank == advance_top_n:
            flags.append("draw_may_be_sufficient")
    elif best_third_places and rank == advance_top_n + 1:
        flags.extend(["third_place_race", "must_avoid_loss", "must_win_pressure"])
    else:
        flags.append("must_win_pressure")
    return flags


def knockout_route_context(rank: int, advance_top_n: int, best_third_places: int) -> str:
    if rank == 1:
        return "小组第一路线；需结合淘汰赛对阵表判断避强队风险"
    if rank <= advance_top_n:
        return "直接晋级路线；可能存在排名选择和轮换权衡"
    if best_third_places and rank == advance_top_n + 1:
        return "第三名路线不确定；需比较其他小组第三名"
    return "当前不在晋级区"


def ensure_team(records: dict[str, TeamRecord], team: str) -> TeamRecord:
    if team not in records:
        records[team] = TeamRecord(team=team)
    return records[team]


def add_result(records: dict[str, TeamRecord], result: dict[str, Any]) -> None:
    home = str(result.get("home_team") or "").strip()
    away = str(result.get("away_team") or "").strip()
    if not home or not away:
        raise ValueError("result must include home_team and away_team")
    try:
        home_goals = int(result["home_goals"])
        away_goals = int(result["away_goals"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{home} vs {away}: result must include integer home_goals and away_goals") from exc

    home_record = ensure_team(records, home)
    away_record = ensure_team(records, away)
    home_record.played += 1
    away_record.played += 1
    home_record.goals_for += home_goals
    home_record.goals_against += away_goals
    away_record.goals_for += away_goals
    away_record.goals_against += home_goals
    if home_goals > away_goals:
        home_record.wins += 1
        away_record.losses += 1
    elif home_goals == away_goals:
        home_record.draws += 1
        away_record.draws += 1
    else:
        home_record.losses += 1
        away_record.wins += 1


def remaining_by_team(fixtures: list[dict[str, Any]]) -> dict[str, int]:
    remaining: dict[str, int] = {}
    for fixture in fixtures:
        for key in ("home_team", "away_team"):
            team = str(fixture.get(key) or "").strip()
            if team:
                remaining[team] = remaining.get(team, 0) + 1
    return remaining


def standings_for_group(group: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    records: dict[str, TeamRecord] = {}
    for team in group.get("teams", []) or []:
        ensure_team(records, str(team).strip())
    for result in group.get("results", []) or []:
        add_result(records, result)
    remaining = remaining_by_team(group.get("fixtures", []) or [])
    for team in remaining:
        ensure_team(records, team)

    ranked = sorted(
        records.values(),
        key=lambda item: (-item.points, -item.goal_difference, -item.goals_for, item.team),
    )
    advance_top_n = int(rules.get("advance_top_n", 2))
    best_third_places = int(rules.get("best_third_places", 0))
    return {
        "group": group.get("group") or group.get("name") or "未确认",
        "standings": [
            record.as_dict(index, remaining.get(record.team, 0), advance_top_n, best_third_places)
            for index, record in enumerate(ranked, start=1)
        ],
        "fixtures": group.get("fixtures", []) or [],
        "source_status": group.get("source_status", "calculated_from_results"),
    }


def calculate(document: dict[str, Any]) -> dict[str, Any]:
    data = document.get("data", document)
    rules = data.get("qualification_rules") or {}
    groups = data.get("groups") or []
    if not isinstance(groups, list) or not groups:
        raise ValueError("input must include data.groups as a non-empty list")
    return {
        "kind": "competition_context",
        "data": {
            "competition": data.get("competition") or "未确认",
            "observed_at": data.get("observed_at"),
            "source": data.get("source") or {},
            "qualification_rules": {
                "advance_top_n": int(rules.get("advance_top_n", 2)),
                "best_third_places": int(rules.get("best_third_places", 0)),
                "tiebreak_summary": rules.get("tiebreak_summary") or "按来源规则；本地排序默认积分、净胜球、进球数",
            },
            "groups": [standings_for_group(group, rules) for group in groups],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate football group standings and qualification context.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = calculate(document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
