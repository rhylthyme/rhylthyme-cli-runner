# eval-prompts results

Generated: 2026-09-19T19:26:36+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-thanksgiving-one-oven | 1.00/0.67/0.80 | 0.88 | 0.40/0.67 | 1.00 | 0.75/0.43/0.55 | 1.00 | 0.00 | 0.41 |
| **mean (n=1)** | **1.00/0.67/0.80** | **0.88** | **0.40/0.67** | **1.00** | **0.75/0.43/0.55** | **1.00** | **0.00** | **0.41** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-thanksgiving-one-oven`: makespan 21900s vs gold 18480s; critical path overlap 0.43
