#!/usr/bin/env python3
"""Fetch football match data into a normalized snapshot.

The first built-in provider is the Sporttery public-data collector for China
Sports Lottery football. It is intentionally conservative: it reads public
pages or explicit local raw fixtures, saves raw responses, and never attempts
login, captcha, WAF bypassing, or hidden endpoint discovery.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


try:
    from team_context_rules import classify_team_context
except ImportError:  # pragma: no cover - direct package execution fallback
    from scripts.team_context_rules import classify_team_context  # type: ignore


SPORTTERY_FOOTBALL_URL = "https://www.sporttery.cn/jczx/#football"
SPORTTERY_MATCH_LIST_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001"
SNAPSHOT_KIND = "football_snapshot"
DEFAULT_TIMEZONE = "Asia/Shanghai"
MARKET_MAP = {
    "胜平负": "match_result",
    "让球胜平负": "handicap_match_result",
    "比分": "correct_score",
    "总进球": "total_goals",
    "大小球": "over_under",
    "半全场胜平负": "half_time_full_time",
}
POOL_MARKET_MAP = {
    "HAD": ("match_result", "胜平负"),
    "HHAD": ("handicap_match_result", "让球胜平负"),
    "CRS": ("correct_score", "比分"),
    "TTG": ("total_goals", "总进球"),
    "HAFU": ("half_time_full_time", "半全场胜平负"),
}


@dataclass(frozen=True)
class RawResponse:
    url: str
    body: str
    status: str
    notes: str = ""


def _observed_at() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _stamp_for_filename(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z+-]+", "", value.replace(":", ""))


def _ensure_unique(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not create a unique filename for {path}")


def _write_text_unique(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = _ensure_unique(path)
    target.write_text(content, encoding="utf-8")
    return target


def _fetch_url(url: str) -> RawResponse:
    request = Request(
        url,
        headers={
            "User-Agent": "football-betting-assistant/1.0 public-data-snapshot",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read()
            content_type = response.headers.get_content_charset() or "utf-8"
            body = raw.decode(content_type, errors="replace")
            status = "blocked" if _looks_like_waf(body) else "ok"
            notes = "WAF block page returned" if status == "blocked" else ""
            return RawResponse(url=url, body=body, status=status, notes=notes)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        status = "blocked" if exc.code in {401, 403} or _looks_like_waf(body) else "missing"
        return RawResponse(url=url, body=body, status=status, notes=f"HTTP {exc.code}")
    except URLError as exc:
        fallback = _fetch_url_with_curl(url)
        if fallback is not None:
            return fallback
        return RawResponse(url=url, body="", status="missing", notes=str(exc.reason))


def _fetch_url_with_curl(url: str) -> RawResponse | None:
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "--max-time",
                "20",
                "-A",
                "football-betting-assistant/1.0 public-data-snapshot",
                url,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    body = result.stdout
    status = "blocked" if _looks_like_waf(body) else "ok"
    notes = "Fetched with curl fallback"
    if status == "blocked":
        notes = "WAF block page returned"
    return RawResponse(url=url, body=body, status=status, notes=notes)


def _looks_like_waf(body: str) -> bool:
    markers = ("WAF拦截", "腾讯云WAF", "您的请求已中断", "Web应用防护")
    return any(marker in body for marker in markers)


def _source(name: str, url: str, observed_at: str, status: str, raw_file: str | None = None, notes: str = "") -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": name,
        "url": url,
        "observed_at": observed_at,
        "status": status,
    }
    if raw_file:
        item["raw_file"] = raw_file
    if notes:
        item["notes"] = notes
    return item


def _source_ref(name: str, url: str, observed_at: str) -> dict[str, str]:
    return {"name": name, "url": url, "observed_at": observed_at}


def _availability(status: str, reason: str, message: str = "") -> dict[str, str]:
    item = {"status": status, "reason": reason}
    if message:
        item["message"] = message
    return item


def _selection(raw: dict[str, Any]) -> dict[str, Any]:
    odds = raw.get("odds")
    try:
        odds = float(odds) if odds is not None else None
    except (TypeError, ValueError):
        odds = None
    return {
        "name": str(raw.get("name") or raw.get("selection") or "").strip(),
        "odds": odds,
        "source_name": str(raw.get("sourceName") or raw.get("source_name") or raw.get("name") or "").strip(),
        "available": bool(raw.get("available", odds is not None)),
    }


def _market(raw: dict[str, Any], source_ref: dict[str, str]) -> dict[str, Any]:
    source_market_name = str(raw.get("name") or raw.get("market") or raw.get("source_market_name") or "").strip()
    market = MARKET_MAP.get(source_market_name, str(raw.get("canonical") or "unsupported_market"))
    selections = [_selection(item) for item in raw.get("selections", []) if isinstance(item, dict)]
    status = str(raw.get("status") or ("available" if selections else "unknown"))
    reason = str(raw.get("reason") or ("available" if status == "available" else "source_missing"))
    return {
        "market": market if market in set(MARKET_MAP.values()) else "unsupported_market",
        "source_market_name": source_market_name or "unknown",
        "line": raw.get("line"),
        "availability": _availability(status, reason, str(raw.get("message") or "")),
        "selections": selections,
        "source": source_ref,
    }


def _price(value: Any) -> float | None:
    if value in (None, "", "--"):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def _odds_market(pool_code: str, odds: dict[str, Any] | None, pool: dict[str, Any] | None, source_ref: dict[str, str]) -> dict[str, Any]:
    market, source_name = POOL_MARKET_MAP.get(pool_code, ("unsupported_market", pool_code))
    pool_status = str((pool or {}).get("poolStatus") or "")
    has_pool = pool is not None
    is_selling = pool_status.lower() == "selling"
    odds = odds or {}
    selections: list[dict[str, Any]] = []
    line = odds.get("goalLineValue") or odds.get("goalLine")

    if pool_code in {"HAD", "HHAD"}:
        names = ("胜", "平", "负") if pool_code == "HAD" else ("让胜", "让平", "让负")
        values = (odds.get("h"), odds.get("d"), odds.get("a"))
        selections = [
            {"name": name, "odds": _price(value), "source_name": key, "available": _price(value) is not None}
            for name, value, key in zip(names, values, ("h", "d", "a"))
            if _price(value) is not None
        ]
    elif pool_code == "TTG":
        selections = [
            {"name": f"{index}球" if index < 7 else "7+球", "odds": _price(odds.get(f"s{index}")), "source_name": f"s{index}", "available": _price(odds.get(f"s{index}")) is not None}
            for index in range(8)
            if _price(odds.get(f"s{index}")) is not None
        ]
    elif pool_code == "CRS":
        for key, label in (
            ("s01s00", "1:0"), ("s02s00", "2:0"), ("s02s01", "2:1"),
            ("s03s00", "3:0"), ("s03s01", "3:1"), ("s03s02", "3:2"),
            ("s00s00", "0:0"), ("s01s01", "1:1"), ("s02s02", "2:2"),
            ("s00s01", "0:1"), ("s00s02", "0:2"), ("s01s02", "1:2"),
            ("s1sh", "胜其他"), ("s1sd", "平其他"), ("s1sa", "负其他"),
        ):
            price = _price(odds.get(key))
            if price is not None:
                selections.append({"name": label, "odds": price, "source_name": key, "available": True})
    elif pool_code == "HAFU":
        # Sporttery HAFU feeds commonly use first letter for half-time result
        # and second letter for full-time result: h=胜, d=平, a=负.
        for keys, label in (
            (("hh", "h_h", "sHH", "sHh"), "胜胜"),
            (("hd", "h_d", "sHD", "sHd"), "胜平"),
            (("ha", "h_a", "sHA", "sHa"), "胜负"),
            (("dh", "d_h", "sDH", "sDh"), "平胜"),
            (("dd", "d_d", "sDD", "sDd"), "平平"),
            (("da", "d_a", "sDA", "sDa"), "平负"),
            (("ah", "a_h", "sAH", "sAh"), "负胜"),
            (("ad", "a_d", "sAD", "sAd"), "负平"),
            (("aa", "a_a", "sAA", "sAa"), "负负"),
        ):
            source_key = next((key for key in keys if _price(odds.get(key)) is not None), keys[0])
            price = _price(odds.get(source_key))
            if price is not None:
                selections.append({"name": label, "odds": price, "source_name": source_key, "available": True})

    if selections:
        availability = _availability("available", "available")
    elif has_pool and is_selling:
        availability = _availability("unknown", "source_missing", f"{source_name} appears open, but odds were not present in this source.")
    elif has_pool:
        availability = _availability("unavailable", "not_offered", f"{source_name} pool status is {pool_status or 'unknown'}.")
    else:
        availability = _availability("unavailable", "not_offered", f"{source_name} was not listed for this match.")

    return {
        "market": market,
        "source_market_name": source_name,
        "line": line,
        "availability": availability,
        "selections": selections,
        "source": source_ref,
    }


def _team_context(raw: dict[str, Any]) -> dict[str, Any]:
    return classify_team_context(
        competition=str(raw.get("competition") or raw.get("leagueAllName") or raw.get("leagueAbbName") or ""),
        home_team=str(raw.get("homeTeam") or raw.get("home_team") or raw.get("homeTeamAllName") or raw.get("homeTeamAbbName") or ""),
        away_team=str(raw.get("awayTeam") or raw.get("away_team") or raw.get("awayTeamAllName") or raw.get("awayTeamAbbName") or ""),
        explicit_team_type=raw.get("teamType") or raw.get("team_type"),
    )


def _parse_json_raw(body: str, source_ref: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return [], [{"code": "parser_error", "message": "Raw response is not JSON."}]
    if isinstance(payload, dict) and isinstance(payload.get("value"), dict) and isinstance(payload["value"].get("matchInfoList"), list):
        return _parse_sporttery_match_info(payload["value"], source_ref)

    raw_matches = payload.get("matches") if isinstance(payload, dict) else None
    if not isinstance(raw_matches, list):
        return [], [{"code": "parser_error", "message": "JSON response does not contain a matches list."}]
    matches: list[dict[str, Any]] = []
    for index, raw_match in enumerate(raw_matches, start=1):
        if not isinstance(raw_match, dict):
            continue
        provider_id = raw_match.get("id") or raw_match.get("provider_match_id")
        match_no = raw_match.get("matchNo") or raw_match.get("match_no")
        match_id = raw_match.get("match_id") or provider_id or f"sporttery-generated-{index:03d}"
        markets = [
            _market(raw_market, source_ref)
            for raw_market in raw_match.get("markets", [])
            if isinstance(raw_market, dict)
        ]
        team_context = _team_context(raw_match)
        matches.append(
            {
                "match_id": f"sporttery-{match_id}",
                "provider_match_id": str(provider_id) if provider_id is not None else None,
                "match_no": str(match_no) if match_no is not None else None,
                "competition": str(raw_match.get("competition") or "unknown"),
                "kickoff_time": str(raw_match.get("kickoffTime") or raw_match.get("kickoff_time") or ""),
                "timezone": DEFAULT_TIMEZONE,
                "home_team": str(raw_match.get("homeTeam") or raw_match.get("home_team") or ""),
                "away_team": str(raw_match.get("awayTeam") or raw_match.get("away_team") or ""),
                "venue_type": str(raw_match.get("venue_type") or "unknown"),
                "team_type": team_context["team_type"],
                "unsupported_reason": raw_match.get("unsupported_reason") or (team_context["reason"] if team_context["team_type"] == "unsupported" else None),
                "team_context": team_context,
                "markets": markets,
                "source": source_ref,
                "data_confidence": "medium" if markets else "low",
            }
        )
    return matches, []


def _parse_sporttery_match_info(value: dict[str, Any], source_ref: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    matches: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    match_groups = value.get("matchInfoList") or []
    if not isinstance(match_groups, list):
        return [], [{"code": "parser_error", "message": "Sporttery value.matchInfoList is not a list."}]

    for group in match_groups:
        if not isinstance(group, dict):
            continue
        for raw_match in group.get("subMatchList", []) or []:
            if not isinstance(raw_match, dict):
                continue
            match_id = str(raw_match.get("matchId") or "")
            if not match_id:
                errors.append({"code": "parser_error", "message": "Sporttery match missing matchId."})
                continue
            odds_by_pool = {
                str(item.get("poolCode") or "").upper(): item
                for item in raw_match.get("oddsList", []) or []
                if isinstance(item, dict)
            }
            pool_by_code = {
                str(item.get("poolCode") or "").upper(): item
                for item in raw_match.get("poolList", []) or []
                if isinstance(item, dict)
            }
            pool_codes = ["HAD", "HHAD", "CRS", "TTG", "HAFU"]
            markets = [
                _odds_market(pool_code, odds_by_pool.get(pool_code) or raw_match.get(pool_code.lower()), pool_by_code.get(pool_code), source_ref)
                for pool_code in pool_codes
                if pool_code in pool_by_code or pool_code in odds_by_pool or raw_match.get(pool_code.lower()) is not None
            ]
            match_time = str(raw_match.get("matchTime") or "")
            if len(match_time) == 5:
                match_time = f"{match_time}:00"
            kickoff = f"{raw_match.get('matchDate')}T{match_time}+08:00" if raw_match.get("matchDate") and match_time else ""
            team_context = _team_context(raw_match)
            matches.append(
                {
                    "match_id": f"sporttery-{match_id}",
                    "provider_match_id": match_id,
                    "match_no": raw_match.get("matchNumStr"),
                    "competition": str(raw_match.get("leagueAllName") or raw_match.get("leagueAbbName") or "unknown"),
                    "kickoff_time": kickoff,
                    "timezone": DEFAULT_TIMEZONE,
                    "home_team": str(raw_match.get("homeTeamAllName") or raw_match.get("homeTeamAbbName") or ""),
                    "away_team": str(raw_match.get("awayTeamAllName") or raw_match.get("awayTeamAbbName") or ""),
                    "venue_type": "neutral" if "中立" in str(raw_match.get("remark") or "") or "世界杯" in str(raw_match.get("leagueAllName") or "") else "unknown",
                    "team_type": team_context["team_type"],
                    "unsupported_reason": team_context["reason"] if team_context["team_type"] == "unsupported" else None,
                    "team_context": team_context,
                    "markets": markets,
                    "source": source_ref,
                    "data_confidence": "medium" if markets else "low",
                    "notes": str(raw_match.get("remark") or ""),
                }
            )
    return matches, errors


def _build_snapshot(
    *,
    mode: str,
    provider: str,
    observed_at: str,
    sources: list[dict[str, Any]],
    matches: list[dict[str, Any]],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    stamp = _stamp_for_filename(observed_at)
    confidence = "medium" if matches else "low"
    if any(source.get("status") in {"blocked", "missing", "parse_failed"} for source in sources):
        confidence = "low"
    return {
        "kind": SNAPSHOT_KIND,
        "data": {
            "snapshot_id": f"{provider}-football-{stamp}",
            "mode": mode,
            "provider": provider,
            "sport": "football",
            "observed_at": observed_at,
            "timezone": DEFAULT_TIMEZONE,
            "confidence": confidence,
            "sources": sources,
            "matches": matches,
            "errors": errors,
        },
    }


def collect_sporttery_snapshot(raw_input: Path | None, out_dir: Path, save_raw: bool = True) -> tuple[dict[str, Any], Path | None]:
    observed_at = _observed_at()
    stamp = _stamp_for_filename(observed_at)
    source_url = SPORTTERY_MATCH_LIST_URL
    if raw_input:
        body = raw_input.read_text(encoding="utf-8")
        source_url = str(raw_input)
        raw_response = RawResponse(url=source_url, body=body, status="ok")
    else:
        raw_response = _fetch_url(source_url)

    raw_file: Path | None = None
    if save_raw and raw_response.body:
        suffix = ".json" if raw_response.body.lstrip().startswith(("{", "[")) else ".html"
        raw_file = _write_text_unique(out_dir / "raw" / f"sporttery-football-{stamp}-main{suffix}", raw_response.body)

    source_status = raw_response.status
    source_notes = raw_response.notes
    raw_file_text = str(raw_file) if raw_file else None
    source = _source("sporttery", raw_response.url, observed_at, source_status, raw_file_text, source_notes)
    source_ref = _source_ref("sporttery", raw_response.url, observed_at)
    matches: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    if raw_response.status == "blocked":
        errors.append({"code": "waf_blocked", "message": "Sporttery public source blocked the request.", "source": raw_response.url})
    elif raw_response.status == "missing":
        errors.append({"code": "source_missing", "message": raw_response.notes or "Sporttery public source unavailable.", "source": raw_response.url})
    elif raw_response.body.lstrip().startswith(("{", "[")):
        matches, parse_errors = _parse_json_raw(raw_response.body, source_ref)
        errors.extend(parse_errors)
        if parse_errors:
            source["status"] = "parse_failed"
    else:
        # The public landing page often loads match data through front-end
        # fragments. Do not infer fixtures from display text unless the parser
        # has a verified structure.
        errors.append(
            {
                "code": "source_missing",
                "message": "Sporttery page was fetched, but no verified structured football match list was found.",
                "source": raw_response.url,
            }
        )

    snapshot = _build_snapshot(mode="china-lottery", provider="sporttery", observed_at=observed_at, sources=[source], matches=matches, errors=errors)
    return snapshot, raw_file


def write_snapshot(snapshot: dict[str, Any], out_dir: Path) -> Path:
    data = snapshot["data"]
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{data['snapshot_id']}.json"
    target = _ensure_unique(out_dir / filename)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch football match data into a normalized snapshot.")
    parser.add_argument("--mode", choices=["china-lottery", "international-odds", "analysis-only"], default="china-lottery")
    parser.add_argument("--provider", choices=["sporttery"], default="sporttery")
    parser.add_argument("--football", action="store_true", help="Collect football data.")
    parser.add_argument("--out", type=Path, default=Path("data/football/snapshots"))
    parser.add_argument("--raw-input", type=Path, help="Parse a local raw fixture instead of fetching the public page.")
    parser.add_argument("--no-save-raw", action="store_true")
    args = parser.parse_args()

    if not args.football:
        parser.error("--football is required for the first version")
    if args.mode != "china-lottery" or args.provider != "sporttery":
        parser.error("The first version only implements --mode china-lottery --provider sporttery")

    snapshot, raw_file = collect_sporttery_snapshot(args.raw_input, args.out, save_raw=not args.no_save_raw)
    snapshot_path = write_snapshot(snapshot, args.out)
    result = {
        "snapshot_path": str(snapshot_path),
        "raw_file": str(raw_file) if raw_file else None,
        "matches": len(snapshot["data"].get("matches", [])),
        "errors": snapshot["data"].get("errors", []),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not snapshot["data"].get("errors") or snapshot["data"].get("matches") else 2


if __name__ == "__main__":
    raise SystemExit(main())
