# eval-prompts results

Generated: 2026-09-19T20:45:42+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-western-blot-transfer-block | 0.95/1.00/0.98 | 0.86 | 0.44/0.50 | 1.00 | 0.61/0.87/0.71 | 0.72 | 0.00 | 0.04 |
| **mean (n=1)** | **0.95/1.00/0.98** | **0.86** | **0.44/0.50** | **1.00** | **0.61/0.87/0.71** | **0.72** | **0.00** | **0.04** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-western-blot-transfer-block`: makespan 65100s vs gold 78120s
