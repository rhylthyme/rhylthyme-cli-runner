# eval-prompts results

Generated: 2026-09-19T19:24:53+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.72/0.84 | 0.92 | 0.60/0.50 | 1.00 | 0.46/0.32/0.37 | 0.95 | 0.00 | 0.28 |
| **mean (n=1)** | **1.00/0.72/0.84** | **0.92** | **0.60/0.50** | **1.00** | **0.46/0.32/0.37** | **0.95** | **0.00** | **0.28** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-backyard-barbecue-smoker-grill`: makespan 50580s vs gold 43320s; critical path overlap 0.27
