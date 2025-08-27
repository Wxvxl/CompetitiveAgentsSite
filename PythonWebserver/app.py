# app.py
import os, math, random, pkgutil, importlib, inspect
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

# === import（ game_core/）===
from game_core import Agent, AgentHandler, Game
import game_core.agents as agents_pkg

BASE = Path(__file__).resolve().parent
AGENTS_DIR = Path(agents_pkg.__path__[0])  # game_core/agents
ALLOWED_EXT = {".py"}

app = Flask(__name__)
app.config.update(
    #SECRET_KEY="change-me",
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10MB
)

def discover_agent_classes():
    """List all valid agents in /agents"""
    importlib.invalidate_caches()
    classes = []
    for item in pkgutil.iter_modules([str(AGENTS_DIR)]):
        mod = importlib.import_module(f"{agents_pkg.__name__}.{item.name}")
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, Agent) and cls is not Agent:
                classes.append(cls)
    return classes

def build_agent_pool(agent_classes, min_pool=10):
    """Duplicate instances to reach at least min_pool candidate Agents."""
    if not agent_classes:
        return []
    copies = max(1, math.ceil(min_pool / len(agent_classes)))
    pool, idx = [], 0
    for cls in agent_classes:
        for _ in range(copies):
            name = f"{cls.__name__[:3].lower()}{idx}"
            wrapped = AgentHandler(cls(name=name))
            wrapped.orig_class = cls
            pool.append(wrapped)
            idx += 1
    return pool

@app.route("/", methods=["GET"])
def index():
    names = [c.__name__ for c in discover_agent_classes()]
    return render_template("index.html", agent_names=names)

@app.route("/upload", methods=["POST"])
def upload():
    """Upload .py to game_core/agents/, immediately available."""
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Please select a file")
        return redirect(url_for("index"))
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        flash("Only .py files are allowed")
        return redirect(url_for("index"))

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    (AGENTS_DIR / "__init__.py").touch(exist_ok=True)
    save_path = AGENTS_DIR / secure_filename(f.filename)
    f.save(save_path)
    importlib.invalidate_caches()
    flash(f"Uploaded: {save_path.name}")
    return redirect(url_for("index"))

@app.route("/play", methods=["POST"])
def play():
    """Run one game and return log/errors (JSON)."""
    data = request.get_json(silent=True) or {}
    size = data.get("size")
    # seed = data.get("seed")
    # if seed is not None:
    #     random.seed(int(seed))

    classes = discover_agent_classes()
    if not classes:
        return jsonify(ok=False, log="No Agent class found in game_core/agents/.")

    pool = build_agent_pool(classes, min_pool=10)
    n = int(size) if size else random.randint(5, 10)
    if not (5 <= n <= 10):
        return jsonify(ok=False, log="Number of players must be between 5 and 10.")

    agents = random.sample(pool, n)
    game = Game(agents)
    game.play()
    log = str(game)

    errors = {}
    for a in agents:
        if getattr(a, "errors", 0):
            key = getattr(a, "orig_class", a.__class__).__name__
            errors[key] = errors.get(key, 0) + a.errors
    return jsonify(ok=True, log=log, errors=errors, players=n)

#---run tournament---
import io, re
from pathlib import Path
from contextlib import redirect_stdout
import random as _random

def _run_tournament_via_exec(games: int = 10, seed: int | None = None):
    """
    Execute a modified source code of run_tournament.py without changing it,
    capturing stdout and the generated scores/res_wins/spy_wins results.
    Supports setting number of games and random seed.
    """
    src_path = Path(__file__).resolve().parent / "game_core" / "run_tournament.py"
    code = src_path.read_text(encoding="utf-8")

    # Inject number of games: replace NUMBER_OF_GAMES
    code = re.sub(r"NUMBER_OF_GAMES\s*=\s*\d+", f"NUMBER_OF_GAMES = {int(games)}", code)

    # Disable per-game printing (to avoid log flooding)
    code = re.sub(r"PRINT_GAME_EVENTS\s*=\s*\w+", "PRINT_GAME_EVENTS = False", code)

    # Set random seed (affects player selection, fallback voting, etc.)
    if seed is not None:
        _random.seed(int(seed))

    # Execute source and capture stdout
    g = {}                # execution environment dict (globals/locals shared)
    buf = io.StringIO()   # to collect print()
    with redirect_stdout(buf):
        exec(compile(code, str(src_path), "exec"), g, g)

    stdout = buf.getvalue()

    # Retrieve result objects from execution environment
    scores = g.get("scores")
    if not scores:
        return {"ok": False, "msg": "tournament executed but no scores were produced", "stdout": stdout}

    total_games = scores.get("games", 0)
    res_wins = scores.get("res_wins", 0)
    spy_wins = scores.get("spy_wins", 0)

    # Flatten to className->stats structure for frontend display
    flat_scores = {}
    for k, v in scores.items():
        if k in ("games", "res_wins", "spy_wins"):
            continue
        name = getattr(k, "__name__", str(k))
        flat_scores[name] = v

    return {
        "ok": True,
        "games": total_games,
        "resistance_wins": res_wins,
        "spy_wins": spy_wins,
        "scores": flat_scores,
        #"stdout": stdout,   #raw print output on page, show/download directly
    }


@app.route("/tournament", methods=["POST"])
def tournament():
    data = request.get_json(silent=True) or {}
    games = int(data.get("games", 10))
    seed  = data.get("seed")  # optional

    try:
        result = _run_tournament_via_exec(games=games, seed=seed)
        return jsonify(result)
    except Exception as e:
        return jsonify(ok=False, msg=f"tournament execution failed: {e}")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)