# Rhylthyme CLI Runner

Command-line interface for validating and running Rhylthyme real-time program schedules.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/rhylthyme/rhylthyme-cli-runner.git
cd rhylthyme-cli-runner

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI

```bash
pip install rhylthyme-cli-runner
```

## Getting the Examples

The example programs referenced in this documentation are maintained in a separate repository. To use them:

### Option 1: Clone the Examples Repository Alongside

```bash
# Navigate to the parent directory of rhylthyme-cli-runner
cd ..

# Clone the examples repository
git clone https://github.com/rhylthyme/rhylthyme-examples.git

# Run examples using relative paths
cd rhylthyme-cli-runner
rhylthyme run ../rhylthyme-examples/programs/breakfast_schedule.json
```

### Option 2: Clone Examples as a Subdirectory

```bash
# From within the rhylthyme-cli-runner directory
git clone https://github.com/rhylthyme/rhylthyme-examples.git examples

# Run examples directly
rhylthyme run examples/programs/breakfast_schedule.json
```

### Option 3: Download Individual Examples

```bash
# Download a specific example file
curl -O https://raw.githubusercontent.com/rhylthyme/rhylthyme-examples/main/programs/breakfast_schedule.json

# Run the downloaded file
rhylthyme run breakfast_schedule.json
```

## Quick Start

The Rhylthyme CLI provides commands for working with real-time program schedules defined using the Rhylthyme JSON or YAML schema.

### Validate a Program

Validate a program file against the schema to ensure it's properly formatted:

```bash
# Validate a JSON or YAML program file
rhylthyme validate my_program.json

# Validate with verbose output
rhylthyme validate my_program.json --verbose

# Validate with JSON output for CI/scripting
rhylthyme validate my_program.json --json

# Validate in strict mode (requires all tasks in resourceConstraints)
rhylthyme validate my_program.json --strict
```

### Run a Program

Run a program with an interactive terminal UI for monitoring and controlling execution:

```bash
# Run a program file
rhylthyme run examples/programs/breakfast_schedule.json

# Run with automatic start (no manual trigger needed)
rhylthyme run examples/programs/breakfast_schedule.json --auto-start

# Run with a different time scale (2x faster)
rhylthyme run examples/programs/breakfast_schedule.json --time-scale 2.0

# Run with a specific environment
rhylthyme run examples/programs/breakfast_schedule.json --environment kitchen

# Run without validation (if you're sure the file is valid)
rhylthyme run examples/programs/breakfast_schedule.json --no-validate
```

### Optimize a Program

Create an optimized version of a program to reduce resource contention:

```bash
# Optimize a program and save to new file
rhylthyme plan examples/programs/breakfast_schedule.json optimized_breakfast.json

# Optimize with verbose output
rhylthyme plan examples/programs/breakfast_schedule.json optimized_breakfast.json --verbose
```

### Work with Environments

List and validate environment catalogs:

```bash
# List all available environments
rhylthyme environments

# List environments in JSON format
rhylthyme environments --format json

# Validate all environment files
rhylthyme validate-environments

# Show information about a specific environment type
rhylthyme environment-info kitchen
```

## Program File Examples

### Simple Breakfast Schedule

```json
{
  "programId": "breakfast-schedule",
  "name": "Breakfast Schedule",
  "description": "Coordinated breakfast preparation",
  "environmentType": "kitchen",
  "startTrigger": {
    "type": "manual"
  },
  "tracks": [
    {
      "trackId": "eggs",
      "name": "Scrambled Eggs",
      "steps": [
        {
          "stepId": "crack-eggs",
          "name": "Crack and Whisk Eggs",
          "startTrigger": {
            "type": "programStart"
          },
          "duration": {
            "type": "fixed",
            "seconds": 60
          }
        }
      ]
    }
  ],
  "resourceConstraints": [
    {
      "task": "stove-burner",
      "maxConcurrent": 2,
      "description": "Maximum stove burners"
    }
  ],
  "version": "1.0.0"
}
```

## Interactive UI Controls

When running a program, the interactive UI provides these controls:

- **Space**: Start/stop the program
- **Enter**: Trigger manual steps
- **Arrow keys**: Navigate between steps
- **q**: Quit the program
- **r**: Refresh the display
- **s**: Sort by different criteria

## Command Reference

### `rhylthyme validate`

Validates program files against the schema.

**Options:**
- `--schema PATH`: Path to schema file (default: built-in schema)
- `--verbose, -v`: Show detailed validation information

### `rhylthyme run`

Runs programs with interactive terminal UI.

**Options:**
- `--schema PATH`: Path to schema file (default: built-in schema)
- `-e, --environment TEXT`: Environment ID to use
- `--time-scale FLOAT`: Time scale factor (default: 1.0)
- `--validate / --no-validate`: Validate before running (default: True)
- `--auto-start`: Automatically start without manual trigger

### `rhylthyme plan`

Optimizes program schedules to reduce resource contention.

**Options:**
- `--verbose, -v`: Show detailed planning information

### `rhylthyme environments`

Lists available environment catalogs.

**Options:**
- `--format, -f`: Output format (table, json, yaml)

### `rhylthyme validate-environments`

Validates environment catalog files.

**Options:**
- `--environments-dir PATH`: Directory containing environment files
- `--verbose, -v`: Show detailed validation information

### `rhylthyme environment-info`

Shows information about a specific environment type.

### `rhylthyme eval-prompts`

Scores agent-authored programs against the expert gold set. See
"Evaluating prompts" below for the full flag list.

## Evaluating prompts

`eval-prompts` measures how well a prompt gets a model to author a
Rhylthyme program. It compares a predicted program with the expert gold
program of the same slug in `rhylthyme-examples/gold/` and reports
per-component precision/recall: steps, durations, resources, actors,
relationships (triggers), track Rand index, an end-to-end pass and the
unsupported-step rate.

Two modes:

```bash
# Offline: score programs already on disk (no model calls, no cost).
rhylthyme eval-prompts --score-only \
  --gold ../rhylthyme-examples/gold --predicted /tmp/predicted

# Live: render a prompt pattern per gold source, call a model, extract
# the program JSON, validate it, score it.
rhylthyme eval-prompts \
  --gold ../rhylthyme-examples/gold \
  --model claude-haiku-4-5-20251001 --patterns baseline,four-turn
```

**Patterns** (`--list-patterns`):

| pattern | what it sends |
|---|---|
| `baseline` | The single `plan_schedule` message the MCP server sent before Phase 3, frozen in `eval/patterns/baseline.py` so the committed numbers stay reproducible. |
| `four-turn` | The four messages `plan_schedule` sends today, byte-copied from `rhylthyme-server/mcp-api/prompts.js`: T1 read-back → T2 model check → T3 extraction (steps + source spans, no relationships) → T4 relationships (tracks, triggers, the refined dependency question, then the program). |

Both patterns end in the same validate-and-repair loop and get the same
system prompt, so the only variable between them is the shape of the user
turns. `four-turn` also records the paper's 2/1/0 score for T1 and T2 in
`results.json` under `extras` (`t1_score`, `t2_score`): 2 when the reply
carries the expected JSON shape first time, 1 when a single retry turn
recovers it, 0 when it never does — plus `unsupported_step_ids`, the
steps the model itself marked `inferred` in T3.

**Flags**

| Flag | Meaning |
|---|---|
| `--gold PATH` | Gold set directory (required). |
| `--score-only` | Offline mode; needs `--predicted`. |
| `--predicted PATH` | Directory of predicted programs (`<slug>.json` or `<slug>/program.json`). |
| `--model ID` | Model id for a live run (required unless `--score-only`). Pin it; do not let it drift. |
| `--patterns NAMES` | Comma-separated prompt patterns (default `baseline`). `--list-patterns` prints the registry. |
| `--only SLUGS` | Comma-separated gold slugs to run; applied before `--limit`. |
| `--limit N` | Run only the first N gold programs (slug order). |
| `--concurrency N` | Programs run in parallel (default 1). |
| `--from-cache` | Never call the model: replay cached responses, and fail loudly on a missing key. |
| `--cache-dir PATH` | Where raw responses are cached (default `<out>/cache`). |
| `--max-fix-iterations N` | How many times Python-validator findings are sent back as the next user turn (default 2; 0 disables the fix loop). |
| `--max-tokens N` | `max_tokens` per model call (default 16000). |
| `--write-baseline PATH` | Also write `{model, pattern, date, git_note, results}` there. |
| `--out PATH` | Where `results.json`, `results.md`, `responses/` and `predicted/` are written (default `./eval-results`). |
| `--format table\|json` | What to print to stdout. |
| `--skip-js` | Skip the JavaScript validator even when `node` is available. |
| `--threshold FLOAT` | Minimum source-span overlap for two steps to match (default 0.5). |
| `--verbose, -v` | Per-program breakdown under the table. |

**Sub-command** `eval-prompts compare` gates a run against the committed
numbers instead of printing them:

| Flag | Meaning |
|---|---|
| `--baseline FILE` | The stored reference. Use `eval/four-turn.json` — that is what ships. |
| `--results FILE` | `results.json` from the run under test. |
| `--rel-f1-drop N` | Largest tolerated fall in relationships F1, in points (default 5). |
| `--e2e-drop N` | Largest tolerated fall in the end-to-end pass rate, in points (default 0: any drop fails). |
| `--allow-missing` | Do not fail when the results file is missing a program the reference has. |
| `--format table\|json` | Diff table, or the same comparison as JSON. |

**Cost.** A live run spends real money: one call per turn per gold
program, plus one per retry and one per fix iteration. The published
baseline run cost **$1.10** for 24 programs and 49 calls on
`claude-haiku-4-5-20251001` (358k input / 148k output tokens); the
four-turn run over the same 24 cost **$2.20** for 111 calls (969k / 246k)
— four turns instead of one, each carrying the whole conversation so far.
The run prints its own token totals and an estimated cost from the price
table in `src/rhylthyme_cli_runner/eval/llm.py` (prices as of
2026-06-24); an unpriced model reports `unknown` instead of a number.
`--limit`/`--only` keep a trial run cheap.

**Cache.** Every call is cached under `--cache-dir` (default
`<out>/cache`) keyed by sha256 of the model, the pattern name, the system
prompt and the full message list, so each turn of a multi-turn pattern is
cached separately and re-scoring never re-spends. `--from-cache` replays
and refuses to call the API; a missing key is an error naming the slug and
the key. The committed cache for both published runs is `eval/cache/`
(1.44 MB, 160 files). Only the completion is replayed, so the committed
files keep the completion in full and record the prompt side as digests
(`system_sha256`, `messages_sha256`) plus a role/length shape — the cache
is in the repository, so it is kept small on purpose.

**Reading the table.** One row per program, then a mean row:

```
program                               steps P/R/F1    dur acc  res P/R    actors  rel P/R/F1      tracks RI  e2e   unsupp
kitchen-weeknight-stir-fry            1.00/0.87/0.93  1.00     0.00/0.00  1.00    0.62/0.47/0.53  0.97       0.00  0.19
```

- `steps` — matched by source-span overlap ≥ `--threshold`, else by
  normalised name. Precision near 1.00 with low recall means the model
  wrote real steps but far fewer of them than the expert did (it lumps).
- `dur acc` — of matched steps, how many got the duration kind and value right.
- `res P/R` — `resourceConstraints[].task` names.
- `actors` — program `actors` count (1 or 0).
- `rel P/R/F1` — triggers: same owning step, same anchor step, same type,
  offset within 10 %. This is the number the four-turn work in Phase 3
  has to move; the paper this work follows found relationships are the
  weak component, and the baseline agrees.
- `tracks RI` — Rand index of the step-to-track partition.
- `e2e` — passes both validators, makespan within 10 % of gold, critical
  chain shares ≥ 50 % of gold's steps.
- `unsupp` — predicted steps with no gold match and no locatable span, as
  a share of predicted steps. Not counted as errors (PRD open question 4).

A program whose reply carried no parseable program, or one that still
fails the validator after the fix loop, is scored zero on every component
and listed under the table, so a failed run lowers the mean instead of
shrinking the sample.

**`eval/baseline.json`** and **`eval/four-turn.json`** are the committed
numbers, in the same shape: the model pin, the pattern, the date, a git
note for the commit they were produced from, and the full per-program
results. `eval/four-turn.json` is the one CI gates on — it is the pattern
`plan_schedule` ships; `eval/baseline.json` is kept as the historical
single-message number so this table can show what the four turns bought.

### Published numbers

All 24 gold programs, `--max-fix-iterations 2`, `--concurrency 3`, both
patterns on the same model on the same day.

**`baseline` pattern, `claude-haiku-4-5-20251001`, 2026-09-14**
(49 calls, $1.10):

| domain | n | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|---|
| kitchen | 10 | 0.90/0.43/0.56 | 0.88 | 0.50/0.48 | 0.90 | 0.38/0.20/0.25 | 0.78 | 0.00 | 0.47 |
| laboratory | 6 | 0.83/0.24/0.37 | 0.81 | 0.67/0.64 | 1.00 | 0.36/0.10/0.15 | 0.81 | 0.00 | 0.76 |
| event | 4 | 1.00/0.66/0.78 | 0.97 | 0.47/0.39 | 0.25 | 0.47/0.32/0.37 | 0.90 | 0.25 | 0.37 |
| fitness | 4 | 0.75/0.11/0.17 | 0.75 | 0.69/0.69 | 0.75 | 0.42/0.05/0.08 | 0.75 | 0.25 | 0.89 |
| **overall** | **24** | **0.88/0.37/0.48** | **0.85** | **0.57/0.54** | **0.79** | **0.39/0.17/0.22** | **0.80** | **0.08** | **0.60** |

**`four-turn` pattern, same model, same 24 programs, 2026-09-14**
(111 calls, $2.20; T1 and T2 scored 2 on every program, no retries):

| domain | n | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|---|
| kitchen | 10 | 0.94/0.98/0.96 | 0.94 | 0.58/0.59 | 1.00 | 0.68/0.67/0.67 | 0.94 | 0.60 | 0.01 |
| laboratory | 6 | 0.84/0.99/0.91 | 0.85 | 0.57/0.56 | 0.83 | 0.59/0.61/0.59 | 0.90 | 0.67 | 0.01 |
| event | 4 | 0.93/0.99/0.95 | 0.96 | 0.39/0.39 | 0.50 | 0.65/0.68/0.66 | 0.91 | 0.50 | 0.01 |
| fitness | 4 | 0.93/0.76/0.83 | 0.94 | 0.70/0.66 | 0.75 | 0.66/0.48/0.55 | 0.93 | 0.75 | 0.00 |
| **overall** | **24** | **0.91/0.95/0.92** | **0.92** | **0.56/0.56** | **0.83** | **0.65/0.62/0.63** | **0.93** | **0.62** | **0.01** |

**Baseline vs four-turn, means over all 24 programs:**

| metric | baseline | four-turn | change |
|---|---|---|---|
| steps precision | 0.88 | 0.91 | +0.04 |
| steps recall | 0.37 | 0.95 | +0.58 |
| steps F1 | 0.48 | 0.92 | +0.44 |
| durations accuracy | 0.85 | 0.92 | +0.06 |
| resources P/R | 0.57/0.54 | 0.56/0.56 | −0.00/+0.02 |
| actors accuracy | 0.79 | 0.83 | +0.04 |
| **relationships F1** | **0.22** | **0.63** | **+0.41** |
| tracks Rand index | 0.80 | 0.93 | +0.12 |
| **end-to-end pass** | **0.08** | **0.62** | **+0.54** |
| unsupported-step rate | 0.60 | 0.01 | −0.59 |
| calls / cost | 49 / $1.10 | 111 / $2.20 | ×2.3 / ×2.0 |

The hypothesis holds on both numbers the PRD names, and by more on 24
programs than it did on the first 6: relationship F1 nearly triples
(0.22 → 0.63) and the end-to-end pass rate goes from 2/24 to 15/24.
The mechanism is extraction, not inference. The single-message prompt
lumps a source into just over a third of the steps the expert wrote
(recall 0.37) and fills the gaps with work the text does not support
(unsupported rate 0.60), so there is little left for a trigger to point
at — and its one end-to-end failure mode, a program that never passed the
validator at all, is the run's only missing prediction
(`kitchen-two-burner-three-course-dinner`, scored zero). Asking for the
steps and their source spans *before* any relationship exists raises
recall to 0.95 and all but eliminates unsupported steps (0.01); tracks
and triggers then follow (Rand index 0.80 → 0.93). The effect is largest
where the source is longest and most repetitive: baseline recall is 0.11
on the four fitness programs (interval sets it collapses into one step)
and 0.24 in the lab, and four-turn lifts both above 0.75. Resource
constraints are the one component the four turns do not move — naming
what a step occupies is a vocabulary problem, not a structure problem —
and actors stay a coin-flip on the event and fitness sources, where the
expert counts people the text never numbers.

**Regression policy / re-baselining.** CI re-runs the `four-turn` pattern
on the pinned model and fails on a relationships-F1 drop of more than 5
points or **any** end-to-end pass-rate drop against
`eval/four-turn.json`:

```bash
rhylthyme eval-prompts compare \
  --baseline eval/four-turn.json --results eval-results/results.json \
  --rel-f1-drop 5 --e2e-drop 0
```

It prints a metric-by-metric diff, names the programs that moved, warns
(rather than fails) when the two files disagree about the model, and
exits 1 on a regression. Growing the gold set is not a regression; a
program the results file is missing is, because a program that was not
run cannot be said not to have regressed (`--allow-missing` waives it).
Never widen a threshold to land a merge. Re-baseline quarterly to rotate
the model pin, and always in a single commit that updates the pin, both
JSON files, the cache and this table — see
[`development/contributing.md`](https://rhylthyme.com/docs/development/contributing/)
for the procedure.

Reproduce both patterns, all 24 programs, without spending anything:

```bash
rhylthyme eval-prompts --gold ../rhylthyme-examples/gold \
  --model claude-haiku-4-5-20251001 --patterns baseline,four-turn \
  --concurrency 3 --max-fix-iterations 2 \
  --from-cache --cache-dir eval/cache --out /tmp/eval-replay
```

**Prompt under test.** `eval/patterns/four_turn.py` holds byte-identical
Python copies of the four templates in
`rhylthyme-server/mcp-api/prompts.js`, so the prompt the harness measures
is the prompt the MCP server ships. A parity test extracts the JS exports
with `node` and fails on any drift; check it by hand with

```bash
python -m rhylthyme_cli_runner.eval.patterns.four_turn
```

`eval/patterns/baseline.py` is frozen at the single-message prompt as of
Phase 2 and is deliberately *not* in step with today's `index.js`; that
is what keeps `eval/baseline.json` reproducible from the cache.
`eval/patterns/baseline.md` is its rendered copy (server `instructions` +
`rhylthyme://guide/authoring` + the `plan_schedule` message), regenerated
with `python -m rhylthyme_cli_runner.eval.patterns.baseline`; a test
fails if it goes stale.

**Tests.** The harness is unit-tested against a fake client; nothing in
`make test` calls an API. The one real-API test carries the `llm` marker
and is skipped unless `RHYLTHYME_EVAL_LIVE=1`:

```bash
make test-unit                 # excludes llm
RHYLTHYME_EVAL_LIVE=1 pytest -m llm      # one real call, opt in
```

## Development

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`

## License

Apache License 2.0
