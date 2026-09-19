# eval-prompts results

Generated: 2026-09-19T19:58:59+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-thanksgiving-one-oven | 0.96/0.92/0.94 | 0.82 | 0.75/1.00 | 1.00 | 0.70/0.68/0.69 | 0.98 | 0.00 | 0.00 |
| **mean (n=1)** | **0.96/0.92/0.94** | **0.82** | **0.75/1.00** | **1.00** | **0.70/0.68/0.69** | **0.98** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-thanksgiving-one-oven`: makespan 20880s vs gold 18480s
