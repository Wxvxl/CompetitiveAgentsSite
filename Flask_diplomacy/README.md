# Flask Diplomacy Runner

This lightweight Flask application exposes the Diplomacy batch runner
(`run_all_agents_v1.py`) over HTTP so you can trigger the existing scenarios
from a browser or another service.

## Setup

1. Create/activate your preferred virtual environment.
2. Install dependencies (adds Flask on top of the original project
   requirements):

   ```bash
   pip install -r "the_diplomacy /requirements.txt"
   ```

## Usage

To start the server in development mode:

cd to Flask_diplomacy

run:
FLASK_RUN_WITH_THREADS=0 flask --app app run --debug --no-reload

Then open `http://127.0.0.1:5000/` to access a simple UI that lists detected
`agent_*.py` files, lets you choose a scenario/repeat count, and shows the JSON
output returned by the `/agents/run` endpoint.


### Batch Runner (`the_diplomacy/run_all_agents_v1.py`)

- discovers every `agent_*.py`, loads each student agent class, and
  executes the selected scenario from `test.py`, optionally writing results to
  JSON/CSV under `the_diplomacy/results/`.
- `python the_diplomacy/run_all_agents_v1.py` (adjust `SCENARIO_NAME`
  or pass `repeat_nums` by editing the call site as needed).

### Result Analysis (`the_diplomacy/analyze_results.py`)

- parses the `printed_result` field produced by the batch runner
  and summarises the `ALL` line for quick comparison(could be used for ranking list).

