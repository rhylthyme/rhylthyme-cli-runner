# eval-prompts results

Generated: 2026-09-19T20:17:06+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-soup-and-salad-lunch | 1.00/0.20/0.33 | 0.67 | 0.25/0.25 | 1.00 | 0.00/0.00/0.00 | 0.67 | 0.00 | 0.81 |
| **mean (n=1)** | **1.00/0.20/0.33** | **0.67** | **0.25/0.25** | **1.00** | **0.00/0.00/0.00** | **0.67** | **0.00** | **0.81** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-soup-and-salad-lunch`: makespan 3600s vs gold 4080s; critical path overlap 0.14
