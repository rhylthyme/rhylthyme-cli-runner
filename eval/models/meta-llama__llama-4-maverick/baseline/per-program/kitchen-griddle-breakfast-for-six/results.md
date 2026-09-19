# eval-prompts results

Generated: 2026-09-19T19:38:04+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-griddle-breakfast-for-six | 1.00/0.53/0.69 | 0.90 | 0.83/0.83 | 1.00 | 0.67/0.35/0.46 | 1.00 | 0.00 | 0.38 |
| **mean (n=1)** | **1.00/0.53/0.69** | **0.90** | **0.83/0.83** | **1.00** | **0.67/0.35/0.46** | **1.00** | **0.00** | **0.38** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-griddle-breakfast-for-six`: makespan 4500s vs gold 3840s; critical path overlap 0.12
