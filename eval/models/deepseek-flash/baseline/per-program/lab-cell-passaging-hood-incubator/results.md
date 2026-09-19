# eval-prompts results

Generated: 2026-09-19T17:02:14+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-cell-passaging-hood-incubator | 1.00/0.19/0.32 | 1.00 | 1.00/0.83 | 1.00 | 0.75/0.12/0.20 | 1.00 | 0.00 | 0.67 |
| **mean (n=1)** | **1.00/0.19/0.32** | **1.00** | **1.00/0.83** | **1.00** | **0.75/0.12/0.20** | **1.00** | **0.00** | **0.67** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-cell-passaging-hood-incubator`: makespan 61800s vs gold 76260s; critical path overlap 0.40
