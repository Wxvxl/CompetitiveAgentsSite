
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
├── agent_123456.py         # Student agent file
├── agent_654321.py         # Student agent file
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
from contextlib import redirect_stdout
from pathlib import Path
from typing import Type

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
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
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

# ============== main ==============
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # load test.py and scenarios
    if not TEST_PATH.exists():
        print(f"[ERROR] test.py not found: {TEST_PATH}", file=sys.stderr)
        sys.exit(1)
    test_mod = load_module("test", TEST_PATH)
    scenario_fn = get_scenario_fn(test_mod, SCENARIO_NAME)

    # collect student agent files
    agent_files = [p for p in sorted(AGENTS_DIR.glob(INCLUDE_GLOB)) if p.name not in EXCLUDE_NAMES]
    if not agent_files:
        print("[WARN] No agent_*.py found.")
        return

    results = []
    print(f"[INFO] Scenario = {SCENARIO_NAME}")
    for idx, path in enumerate(agent_files, 1):
        student = path.stem.replace("agent_", "")
        print(f"[{idx}/{len(agent_files)}] {path.name} -> Student={student}")
        try:
            mod = load_module(f"{student}_mod", path)
            cls = get_student_agent_cls(mod)
            # get test result
            buf = io.StringIO()
            with redirect_stdout(buf):
                scenario_fn(cls)
            printed = buf.getvalue().strip()
            results.append({"student": student, "filename": path.name, "printed_result": printed})
            print("   => OK")
        except Exception as e:
            msg = f"[ERROR] {type(e).__name__}: {e}"
            results.append({"student": student, "filename": path.name, "printed_result": msg})
            print("   => FAIL:", msg)

    # save results
    jpath = OUTPUT_DIR / f"results_{SCENARIO_NAME}.json"
    cpath = OUTPUT_DIR / f"results_{SCENARIO_NAME}.csv"
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(cpath, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student", "filename", "printed_result"])
        for r in results:
            w.writerow([r["student"], r["filename"], r["printed_result"].replace("\n", "\\n")])

    print("\n[DONE] Saved:")
    print(" JSON:", jpath)
    print(" CSV :", cpath)

if __name__ == "__main__":
    main()