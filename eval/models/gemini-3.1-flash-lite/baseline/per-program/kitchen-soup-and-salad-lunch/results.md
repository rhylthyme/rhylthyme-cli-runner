# eval-prompts results

Generated: 2026-09-19T17:18:46+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-soup-and-salad-lunch | 1.00/0.40/0.57 | 1.00 | 0.50/0.50 | 1.00 | 0.33/0.12/0.17 | 0.73 | 0.00 | 0.54 |
| **mean (n=1)** | **1.00/0.40/0.57** | **1.00** | **0.50/0.50** | **1.00** | **0.33/0.12/0.17** | **0.73** | **0.00** | **0.54** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-soup-and-salad-lunch`: makespan 5640s vs gold 4080s; critical path overlap 0.14
