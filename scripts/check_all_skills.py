#!/usr/bin/env python3
"""Run available checks for every top-level skill in this repository."""

from __future__ import annotations

import pathlib
import subprocess
import sys


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


def run(command: list[str], cwd: pathlib.Path) -> int:
    print(f"\n$ {' '.join(command)}")
    return subprocess.run(command, cwd=cwd, text=True).returncode


def main() -> int:
    skills = discover_skills()
    if not skills:
        print("No top-level skills found.")
        return 1

    failed = False
    for skill in skills:
        print(f"\n== {skill.name} ==")

        test_script = skill / "tests" / "test_scripts.py"
        if test_script.is_file():
            failed = run([sys.executable, str(test_script)], ROOT) != 0 or failed

        acceptance_script = skill / "scripts" / "run_acceptance_checks.py"
        if acceptance_script.is_file():
            failed = run([sys.executable, str(acceptance_script)], ROOT) != 0 or failed

        if not test_script.is_file() and not acceptance_script.is_file():
            print("No checks found for this skill.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
