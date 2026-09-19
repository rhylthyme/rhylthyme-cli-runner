# eval-prompts results

Generated: 2026-09-19T17:13:05+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.67/0.80 | 0.75 | 0.33/0.33 | 1.00 | 0.75/0.47/0.58 | 0.91 | 0.00 | 0.25 |
| **mean (n=1)** | **1.00/0.67/0.80** | **0.75** | **0.33/0.33** | **1.00** | **0.75/0.47/0.58** | **0.91** | **0.00** | **0.25** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-backyard-barbecue-smoker-grill`: makespan 57780s vs gold 43320s; critical path overlap 0.45
