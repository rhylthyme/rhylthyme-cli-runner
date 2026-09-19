# eval-prompts results

Generated: 2026-09-19T19:23:51+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-griddle-breakfast-for-six | 1.00/0.58/0.73 | 0.91 | 0.71/0.83 | 1.00 | 0.45/0.22/0.29 | 0.95 | 0.00 | 0.31 |
| **mean (n=1)** | **1.00/0.58/0.73** | **0.91** | **0.71/0.83** | **1.00** | **0.45/0.22/0.29** | **0.95** | **0.00** | **0.31** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-griddle-breakfast-for-six`: makespan 32400s vs gold 3840s; critical path overlap 0.00
