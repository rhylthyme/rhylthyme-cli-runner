# eval-prompts results

Generated: 2026-09-19T20:42:41+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-thanksgiving-one-oven | 0.89/1.00/0.94 | 0.79 | 0.60/1.00 | 1.00 | 0.51/0.71/0.60 | 0.91 | 0.00 | 0.10 |
| **mean (n=1)** | **0.89/1.00/0.94** | **0.79** | **0.60/1.00** | **1.00** | **0.51/0.71/0.60** | **0.91** | **0.00** | **0.10** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-thanksgiving-one-oven`: makespan 20700s vs gold 18480s; critical path overlap 0.43
