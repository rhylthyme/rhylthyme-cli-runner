# eval-prompts results

Generated: 2026-09-19T20:01:28+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-weeknight-stir-fry | 1.00/0.73/0.85 | 1.00 | 0.00/0.00 | 1.00 | 0.58/0.41/0.48 | 0.93 | 0.00 | 0.21 |
| **mean (n=1)** | **1.00/0.73/0.85** | **1.00** | **0.00/0.00** | **1.00** | **0.58/0.41/0.48** | **0.93** | **0.00** | **0.21** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-weeknight-stir-fry`: makespan 2640s vs gold 2070s
