#!/usr/bin/env python3
"""Run lightweight structural checks for every top-level skill in this repository."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
IGNORED_DIRS = {
    ".agent",
    ".agents",
    ".claude",
    ".git",
    ".idea",
    ".pi",
    "scripts",
}


def discover_skills() -> list[pathlib.Path]:
    skills: list[pathlib.Path] = []
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir() or child.name in IGNORED_DIRS:
            continue
        if (child / "SKILL.md").is_file():
            skills.append(child)
    return skills


def main() -> int:
    skills = discover_skills()
    if not skills:
        print("No top-level skills found.")
        return 1

    failed = False
    for skill in skills:
        print(f"\n== {skill.name} ==")
        required = [skill / "SKILL.md", skill / "README.md"]
        missing = [path.name for path in required if not path.is_file()]
        if missing:
            failed = True
            print(f"Missing required files: {', '.join(missing)}")
        else:
            print("Required files present.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
