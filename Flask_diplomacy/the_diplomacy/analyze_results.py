#!/usr/bin/env python3
"""
Utilities for parsing Diplomacy batch-run JSON results (focus on the ALL summary).

Usage
-----
1. Direct execution – prints a JSON summary to stdout:
       python analyze_results.py --file results/results_Scenario1.json --top 5

2. Import from Python (Flask views, scripts, notebooks):
       from the_diplomacy.analyze_results import analyze_all_summary
       summary = analyze_all_summary(Path("results/results_Scenario1.json"), top_n=5)

3. HTTP endpoints (provided by ``app.py``):
       GET  /results/list       -> {"ok": true, "files": [...]}
       POST /results/analyze    body {"filename": "results_Scenario1.json", "top": 10}
   The frontend uses these to populate the dropdown and render the formatted table.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

RESULTS_DIR = Path(__file__).resolve().parent / "results"
ALL_LINE = re.compile(
    r"^ALL: SCs - (?P<sc>[\d.]+)±(?P<std>[\d.]+), "
    r"Wins - (?P<wins>[\d.]+)%, Survives - (?P<survives>[\d.]+)%, "
    r"Defeats - (?P<defeats>[\d.]+)%$"
)


@dataclass
class AllStats:
    sc_mean: float
    sc_std: float
    win_rate: float
    survive_rate: float
    defeat_rate: float


@dataclass
class AgentOverall:
    student: str
    filename: str
    stats: AllStats


def parse_all(lines: Iterable[str]) -> AllStats | None:
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = ALL_LINE.match(line)
        if match:
            groups = match.groupdict()
            return AllStats(
                sc_mean=float(groups["sc"]),
                sc_std=float(groups["std"]),
                win_rate=float(groups["wins"]),
                survive_rate=float(groups["survives"]),
                defeat_rate=float(groups["defeats"]),
            )
    return None


def parse_entry(entry: Dict[str, str]) -> Tuple[AgentOverall | None, str | None]:
    printed = entry["printed_result"].strip()
    if printed.startswith("[ERROR]") or not printed:
        return None, printed or "[ERROR] Empty output"

    stats = parse_all(printed.splitlines())
    if not stats:
        return None, "[ERROR] 'ALL' summary not found"

    return AgentOverall(entry["student"], entry["filename"], stats), None


def list_result_files(directory: Path = RESULTS_DIR) -> List[str]:
    if not directory.exists():
        return []
    return sorted(p.name for p in directory.glob("results_*.json") if p.is_file())


def analyze_all_summary(path: Path, *, top_n: int | None = None) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        entries = json.load(fh)

    successes: List[AgentOverall] = []
    failures: List[Tuple[str, str]] = []

    for entry in entries:
        agent, error = parse_entry(entry)
        if agent:
            successes.append(agent)
        else:
            failures.append((entry["student"], error or "[ERROR] Unknown"))

    successes.sort(key=lambda a: a.stats.win_rate, reverse=True)
    top_slice = successes if top_n is None else successes[:top_n]

    top_payload = [
        {
            "student": agent.student,
            "filename": agent.filename,
            "wins": agent.stats.win_rate,
            "sc_mean": agent.stats.sc_mean,
            "sc_std": agent.stats.sc_std,
            "survive": agent.stats.survive_rate,
            "defeat": agent.stats.defeat_rate,
        }
        for agent in top_slice
    ]

    average = None
    if successes:
        average = {
            "wins": sum(a.stats.win_rate for a in successes) / len(successes),
            "sc_mean": sum(a.stats.sc_mean for a in successes) / len(successes),
            "sc_std": sum(a.stats.sc_std for a in successes) / len(successes),
            "survive": sum(a.stats.survive_rate for a in successes) / len(successes),
            "defeat": sum(a.stats.defeat_rate for a in successes) / len(successes),
        }

    return {
        "file": path.name,
        "count": len(entries),
        "success_count": len(successes),
        "issue_count": len(failures),
        "top": top_payload,
        "average": average,
        "issues": [{"student": s, "message": msg} for s, msg in failures],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Show top N agents by ALL win rate (default: 10; 0 means show all)",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Custom results file path; defaults to the newest results_*.json",
    )
    args = parser.parse_args()

    target = Path(args.file) if args.file else (
        max((RESULTS_DIR.glob("results_*.json")), default=None)
    )
    if target is None:
        raise FileNotFoundError("No results_*.json files found")

    summary = analyze_all_summary(target, top_n=args.top or None)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
