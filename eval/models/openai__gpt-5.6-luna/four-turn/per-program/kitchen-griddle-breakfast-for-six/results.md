# eval-prompts results

Generated: 2026-09-19T19:24:19+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-griddle-breakfast-for-six | 1.00/0.89/0.94 | 0.94 | 0.86/1.00 | 1.00 | 0.75/0.65/0.70 | 0.97 | 0.00 | 0.06 |
| **mean (n=1)** | **1.00/0.89/0.94** | **0.94** | **0.86/1.00** | **1.00** | **0.75/0.65/0.70** | **0.97** | **0.00** | **0.06** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-griddle-breakfast-for-six`: makespan 5280s vs gold 3840s; critical path overlap 0.25
