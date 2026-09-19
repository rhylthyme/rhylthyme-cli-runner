# eval-prompts results

Generated: 2026-09-19T02:45:05+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-cell-passaging-hood-incubator | 0.91/0.95/0.93 | 0.90 | 0.83/0.83 | 1.00 | 0.59/0.73/0.66 | 1.00 | 0.00 | 0.04 |
| **mean (n=1)** | **0.91/0.95/0.93** | **0.90** | **0.83/0.83** | **1.00** | **0.59/0.73/0.66** | **1.00** | **0.00** | **0.04** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-cell-passaging-hood-incubator`: makespan 61500s vs gold 76260s
