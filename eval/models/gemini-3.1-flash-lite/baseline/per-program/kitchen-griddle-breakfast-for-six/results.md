# eval-prompts results

Generated: 2026-09-19T17:15:57+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-griddle-breakfast-for-six | 1.00/0.42/0.59 | 1.00 | 0.50/0.33 | 1.00 | 0.50/0.17/0.26 | 1.00 | 0.00 | 0.43 |
| **mean (n=1)** | **1.00/0.42/0.59** | **1.00** | **0.50/0.33** | **1.00** | **0.50/0.17/0.26** | **1.00** | **0.00** | **0.43** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-griddle-breakfast-for-six`: makespan 3120s vs gold 3840s; critical path overlap 0.12
