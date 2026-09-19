# eval-prompts results

Generated: 2026-09-19T17:15:04+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-elisa-plate-wash | 1.00/0.91/0.95 | 1.00 | 0.50/0.40 | 1.00 | 0.85/0.68/0.76 | 1.00 | 0.00 | 0.00 |
| **mean (n=1)** | **1.00/0.91/0.95** | **1.00** | **0.50/0.40** | **1.00** | **0.85/0.68/0.76** | **1.00** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-elisa-plate-wash`: makespan 22200s vs gold 76200s
