"""
README – run_all_agents.py
==========================

Overview
--------
run_all_agents.py is a unified entry script for batch testing all student agent
files (agent_*.py). It automates the process of running each student agent
against predefined scenarios in test.py and saves the results.

Project Structure Example
-------------------------
project_root/
│
├── test.py                 # Defines Scenario1 / Scenario2
├── agent_xxx.py         # Student agent file
├── agent_xxxxxx.py         # Student agent file
├── agent_baselines.py      # Baseline agent (excluded from testing)
├── run_all_agents.py       # Entry script
└── results/                # Output folder

Requirements for test.py
------------------------
1. Define scenario functions
   test.py must define Scenario1 and Scenario2, each taking a class
   (e.g., StudentAgent) as the first parameter:

       def Scenario1(player_agent_cls, repeat_nums=10):
           print("Evaluating Scenario 1 ...")
           experiment(
               player_agent=player_agent_cls,
               opponent_agent_pool=[StaticAgent],
               repeat_nums=repeat_nums
           )

       def Scenario2(player_agent_cls, repeat_nums=10):
           print("Evaluating Scenario 2 ...")
           experiment(
               player_agent=player_agent_cls,
               opponent_agent_pool=[RandomAgent, AttitudeAgent, GreedyAgent],
               repeat_nums=repeat_nums
           )

   Note: The argument must be the agent class, not an object, string, or module.

2. Import dependencies
   At the top of test.py, import experiment and baseline agents:

       from experiment import experiment
       from agent_baselines import StaticAgent, RandomAgent, AttitudeAgent, GreedyAgent

3. Avoid running experiments on import
   Do not call experiment(...) directly in the body of test.py.
   Otherwise, experiments will run immediately when imported.
   Wrap all runs inside Scenario1 / Scenario2.

4. Baseline agents must exist
   The scenario functions assume StaticAgent, RandomAgent, AttitudeAgent,
   and GreedyAgent are available. If names differ, adjust the opponent pool.

Usage
-----
1. Select the scenario
   In run_all_agents.py, set:
       SCENARIO_NAME = "Scenario1"   # or "Scenario2"

2. Run the script:
       python run_all_agents.py

3. Check the results
   Results will be stored in the results/ folder:
       results/results_Scenario1.json
       results/results_Scenario1.csv

Programmatic / HTTP usage
-------------------------
- The Flask app exposes ``POST /agents/run`` which forwards to ``run_agents``.
  Example payload: ``{"scenario": "Scenario1", "repeat_nums": 5, "save_outputs": true}``.
- From Python, import the helper and call directly:
      from the_diplomacy.run_all_agents_v1 import run_agents
      payload = run_agents("Scenario1", repeat_nums=5, save_outputs=True)
  The return value matches the JSON emitted by the HTTP endpoint.

Output Format
-------------
JSON Example:
    [
      {
        "student": "123456",
        "filename": "agent_123456.py",
        "printed_result": "Evaluating Scenario 1 ...\\n<printed experiment result>"
      },
      {
        "student": "654321",
        "filename": "agent_654321.py",
        "printed_result": "[ERROR] AttributeError: No StudentAgent-like class found"
      }
    ]

CSV Example:
    student,filename,printed_result
    123456,agent_123456.py,"Evaluating Scenario 1 ...\\n<printed experiment result>"
    654321,agent_654321.py,"[ERROR] AttributeError: No StudentAgent-like class found"

Common Issues
-------------
- [ERROR] AttributeError: No StudentAgent-like class found
    → The student file does not define a StudentAgent class (or alias).

- TypeError: 'str' object is not callable
    → The scenario in test.py is incorrect. Ensure it accepts a class, not a string or instance.

- No agents found
    → Make sure student files follow the naming rule: agent_*.py
"""

import io
import sys
import csv
import json
import importlib.util
import inspect
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type

# ============== Configure ==============
SCENARIO_NAME   = "Scenario2"            # "Scenario1" or "Scenario2"
PROJECT_ROOT    = Path(__file__).resolve().parent
TEST_PATH       = PROJECT_ROOT / "test.py"
AGENTS_DIR      = PROJECT_ROOT
OUTPUT_DIR      = PROJECT_ROOT / "results"
INCLUDE_GLOB    = "agent_*.py"
EXCLUDE_NAMES   = {"agent_baselines.py"}  # exclude non-student agent

# ============== utility methods ==============
def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import {module_name} from {path}")
    module_dir = str(path.parent)
    added_to_path = False
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        added_to_path = True
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    if added_to_path:
        try:
            sys.path.remove(module_dir)
        except ValueError:
            pass
    return mod

def get_student_agent_cls(agent_mod) -> Type:
    for name in ["StudentAgent", "Agent", "MyAgent"]:
        cls = getattr(agent_mod, name, None)
        if isinstance(cls, type):
            return cls
    raise AttributeError(
        "No StudentAgent-like class found (expected one of: "
        "StudentAgent / Agent / MyAgent / AttitudeAgent)"
    )

def get_scenario_fn(test_mod, name: str):
    fn = getattr(test_mod, name, None)
    if not callable(fn):
        raise AttributeError(
            f"{name} is not a callable in test.py. "
            f"Define: def {name}(player_agent_cls, ...): ..."
        )
    return fn


def discover_agents(
    *,
    agents_dir: Path = AGENTS_DIR,
    include_pattern: str = INCLUDE_GLOB,
    exclude_names: Iterable[str] = EXCLUDE_NAMES,
) -> List[str]:
    """Return agent module names (without extension) discovered in the project."""

    files = [
        p for p in sorted(agents_dir.glob(include_pattern))
        if p.name not in set(exclude_names)
    ]
    return [p.stem for p in files]


def discover_scenarios(
    *,
    test_path: Path = TEST_PATH,
    default: Optional[str] = SCENARIO_NAME,
) -> List[str]:
    """Return the list of scenario function names exposed by ``test.py``.

    A scenario function must:
    - reside at module scope in ``test.py``;
    - have a name starting with ``Scenario`` (case-insensitive);
    - be callable and accept at least one positional argument (the agent class).

    Raises
    ------
    FileNotFoundError
        If ``test.py`` does not exist at ``test_path``.
    RuntimeError
        If importing ``test.py`` raised an exception.
    ValueError
        If no valid scenario functions were found.
    """

    if not test_path.exists():
        raise FileNotFoundError(f"test module not found at {test_path}")

    try:
        test_mod = load_module("test_discovery", test_path)
    except Exception as exc:  # noqa: BLE001 propagate details to caller
        raise RuntimeError(f"Failed to import test module {test_path}: {exc}") from exc

    scenario_names: List[str] = []
    for name, func in inspect.getmembers(test_mod, inspect.isfunction):
        if not name.lower().startswith("scenario"):
            continue
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if not params:
            continue
        first = params[0]
        if first.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            continue
        scenario_names.append(name)

    if default and default not in scenario_names:
        scenario_names.append(default)

    if not scenario_names:
        raise ValueError(
            "No scenario functions found in test.py. "
            "Ensure they are named like 'ScenarioX' and accept at least one positional argument."
        )

    deduped = list(dict.fromkeys(scenario_names))
    deduped.sort()
    return deduped

# ============== main ==============
def run_agents(
    scenario_name: str,
    *,
    output_dir: Optional[Path] = None,
    include_pattern: str = INCLUDE_GLOB,
    exclude_names: Iterable[str] = EXCLUDE_NAMES,
    repeat_nums: Optional[int] = None,
    save_outputs: bool = True,
) -> Dict[str, object]:
    """Run all student agents for the given scenario and return structured data.

    Parameters
    ----------
    scenario_name: str
        Name of the scenario function defined in test.py (e.g. "Scenario1").
    output_dir: Path | None
        Directory to store json/csv results when ``save_outputs`` is True.
    include_pattern: str
        Glob used to discover student agent files.
    exclude_names: Iterable[str]
        Filenames to exclude from discovery (baseline agents, etc.).
    repeat_nums: int | None
        Optional repeat count passed to the scenario function if provided.
    save_outputs: bool
        Whether to persist results to disk.

    Returns
    -------
    dict
        A payload containing scenario name, result rows, log messages, and
        optional paths to saved artifacts.
    """

    logs: List[str] = []
    def log(msg: str) -> None:
        logs.append(msg)

    if not TEST_PATH.exists():
        raise FileNotFoundError(f"test.py not found: {TEST_PATH}")

    test_mod = load_module("test", TEST_PATH)
    scenario_fn = get_scenario_fn(test_mod, scenario_name)

    agent_files = [
        p for p in sorted(AGENTS_DIR.glob(include_pattern))
        if p.name not in set(exclude_names)
    ]
    if not agent_files:
        log("[WARN] No agent_*.py found.")
        return {
            "scenario": scenario_name,
            "results": [],
            "logs": logs,
        }

    results: List[Dict[str, str]] = []
    log(f"[INFO] Scenario = {scenario_name}")
    scenario_kwargs = {"repeat_nums": repeat_nums} if repeat_nums is not None else {}

    for idx, path in enumerate(agent_files, 1):
        student = path.stem.replace("agent_", "")
        log(f"[{idx}/{len(agent_files)}] {path.name} -> Student={student}")
        try:
            mod = load_module(f"{student}_mod", path)
            cls = get_student_agent_cls(mod)
            buf = io.StringIO()
            with redirect_stdout(buf):
                scenario_fn(cls, **scenario_kwargs)
            printed = buf.getvalue().strip()
            results.append(
                {
                    "student": student,
                    "filename": path.name,
                    "printed_result": printed,
                }
            )
            log("   => OK")
        except Exception as e:  # noqa: BLE001 broad but intentional to mirror CLI behaviour
            msg = f"[ERROR] {type(e).__name__}: {e}"
            results.append(
                {
                    "student": student,
                    "filename": path.name,
                    "printed_result": msg,
                }
            )
            log(f"   => FAIL: {msg}")

    payload: Dict[str, object] = {
        "scenario": scenario_name,
        "results": results,
        "logs": logs,
    }

    if save_outputs:
        target_dir = output_dir or OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        jpath = target_dir / f"results_{scenario_name}.json"
        cpath = target_dir / f"results_{scenario_name}.csv"
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        with open(cpath, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["student", "filename", "printed_result"])
            for r in results:
                w.writerow([r["student"], r["filename"], r["printed_result"].replace("\n", "\\n")])
        payload["saved_files"] = {"json": jpath, "csv": cpath}

    return payload


def main():
    try:
        payload = run_agents(SCENARIO_NAME)
    except Exception as exc:  # noqa: BLE001 broad for CLI parity
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    for line in payload.get("logs", []):
        print(line)

    saved = payload.get("saved_files")
    if saved:
        print("\n[DONE] Saved:")
        print(" JSON:", saved["json"])
        print(" CSV :", saved["csv"])

if __name__ == "__main__":
    main()
