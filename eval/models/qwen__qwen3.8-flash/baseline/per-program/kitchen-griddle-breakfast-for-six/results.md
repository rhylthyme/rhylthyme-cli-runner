# eval-prompts results

Generated: 2026-09-19T19:53:20+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-griddle-breakfast-for-six | 1.00/0.11/0.19 | 1.00 | 0.43/0.50 | 1.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.90 |
| **mean (n=1)** | **1.00/0.11/0.19** | **1.00** | **0.43/0.50** | **1.00** | **0.00/0.00/0.00** | **1.00** | **0.00** | **0.90** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-griddle-breakfast-for-six`: makespan 4260s vs gold 3840s; critical path overlap 0.00
