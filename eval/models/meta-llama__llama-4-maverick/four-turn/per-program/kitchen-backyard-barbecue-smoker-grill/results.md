# eval-prompts results

Generated: 2026-09-19T19:24:45+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-backyard-barbecue-smoker-grill | 0.95/1.00/0.97 | 0.94 | 0.50/0.50 | 1.00 | 0.63/0.63/0.63 | 0.96 | 0.00 | 0.00 |
| **mean (n=1)** | **0.95/1.00/0.97** | **0.94** | **0.50/0.50** | **1.00** | **0.63/0.63/0.63** | **0.96** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-backyard-barbecue-smoker-grill`: makespan 50640s vs gold 43320s; critical path overlap 0.45
