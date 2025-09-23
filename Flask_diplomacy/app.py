# for run flask without errors
# please use command `FLASK_RUN_WITH_THREADS=0 flask --app app run --debug --no-reload`
# it keeps Flask single-threaded so the Diplomacy engine’s signal-based timeouts stay reliable. 

# ====================================
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from flask import Flask, jsonify, render_template, request

from the_diplomacy.analyze_results import analyze_all_summary, list_result_files


# Ensure Flask's built-in runner stays single-threaded so signal-based timeouts
# inside the game engine keep working.
os.environ.setdefault("FLASK_RUN_WITH_THREADS", "0")

APP_ROOT = Path(__file__).resolve().parent
DIPLOMACY_DIR = APP_ROOT / "the_diplomacy"
RUNNER_PATH = DIPLOMACY_DIR / "run_all_agents_v1.py"
RESULTS_DIR = DIPLOMACY_DIR / "results"

def _load_runner_module():
    if not RUNNER_PATH.exists():
        raise FileNotFoundError(f"Runner module not found at {RUNNER_PATH}")
    spec = importlib.util.spec_from_file_location("the_diplomacy_runner", RUNNER_PATH)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load spec for {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


runner_module = _load_runner_module()

if not hasattr(runner_module, "run_agents"):
    raise AttributeError("Runner module must expose a run_agents function")

if not hasattr(runner_module, "discover_agents"):
    raise AttributeError("Runner module must expose a discover_agents function")

if not hasattr(runner_module, "discover_scenarios"):
    raise AttributeError("Runner module must expose a discover_scenarios function")

run_agents: Callable[..., Dict[str, Any]] = runner_module.run_agents  # type: ignore[attr-defined]
runner_discover_agents: Callable[[], List[str]] = runner_module.discover_agents  # type: ignore[attr-defined]
runner_discover_scenarios: Callable[[], List[str]] = runner_module.discover_scenarios  # type: ignore[attr-defined]
DEFAULT_SCENARIO = getattr(runner_module, "SCENARIO_NAME", "Scenario1")


app = Flask(__name__)


def _serialise_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert non-JSON types (Path, etc.) before jsonify."""
    updated = dict(payload)
    if "saved_files" in updated and updated["saved_files"]:
        updated["saved_files"] = {
            key: str(value) for key, value in updated["saved_files"].items()
        }
    updated["logs"] = updated.get("logs", [])
    return updated


def _require_non_empty(name: str, values: List[str]) -> List[str]:
    if not values:
        raise ValueError(f"Runner module returned no entries from {name}")
    return values


def discover_agents() -> List[str]:
    return _require_non_empty("discover_agents", list(runner_discover_agents()))


def discover_scenarios() -> List[str]:
    return _require_non_empty("discover_scenarios", list(runner_discover_scenarios()))


@app.get("/health")
def health() -> Any:
    return {"status": "ok"}


@app.get("/")
def index() -> Any:
    scenario_error: str | None = None
    agent_error: str | None = None

    try:
        scenarios = discover_scenarios()
    except Exception as exc:  # noqa: BLE001 surface errors to the template
        scenario_error = str(exc)
        scenarios = [DEFAULT_SCENARIO] if DEFAULT_SCENARIO else []

    try:
        agents = discover_agents()
    except Exception as exc:  # noqa: BLE001
        agent_error = str(exc)
        agents = []

    scenario_default = None
    if scenarios:
        scenario_default = (
            DEFAULT_SCENARIO if DEFAULT_SCENARIO in scenarios else scenarios[0]
        )

    return render_template(
        "index.html",
        scenario_default=scenario_default,
        scenarios=scenarios,
        agents=agents,
        scenario_error=scenario_error,
        agent_error=agent_error,
    )


@app.post("/agents/run")
def run_agents_endpoint():
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario") or DEFAULT_SCENARIO
    repeat_nums = data.get("repeat_nums")
    save_outputs = bool(data.get("save_outputs", False))

    try:
        repeat_value = int(repeat_nums) if repeat_nums is not None else None
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "repeat_nums must be an integer"}), 400

    try:
        payload = run_agents(
            scenario_name=scenario,
            repeat_nums=repeat_value,
            save_outputs=save_outputs,
        )
    except Exception as exc:  # noqa: BLE001 broad by design to surface runner errors
        return jsonify({"ok": False, "error": str(exc)}), 400

    serialised = _serialise_payload(payload)
    return jsonify({"ok": True, **serialised})

@app.get("/results/list")
def list_results_endpoint():
    try:
        files = list_result_files(RESULTS_DIR)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500
    return jsonify({"ok": True, "files": files})


@app.post("/results/analyze")
def analyze_results_endpoint():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")
    top_n = data.get("top")

    if not filename:
        return jsonify({"ok": False, "error": "filename is required"}), 400

    candidate = (RESULTS_DIR / filename).resolve()
    if not candidate.is_file() or RESULTS_DIR.resolve() not in candidate.parents:
        return jsonify({"ok": False, "error": "invalid filename"}), 400

    try:
        summary = analyze_all_summary(candidate, top_n=int(top_n) if top_n else None)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, **summary})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=False)
