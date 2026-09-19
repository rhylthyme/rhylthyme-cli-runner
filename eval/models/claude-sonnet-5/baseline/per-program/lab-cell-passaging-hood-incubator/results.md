# eval-prompts results

Generated: 2026-09-19T02:49:57+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-cell-passaging-hood-incubator | 1.00/0.24/0.38 | 1.00 | 0.80/0.67 | 1.00 | 0.60/0.12/0.19 | 1.00 | 0.00 | 0.58 |
| **mean (n=1)** | **1.00/0.24/0.38** | **1.00** | **0.80/0.67** | **1.00** | **0.60/0.12/0.19** | **1.00** | **0.00** | **0.58** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-cell-passaging-hood-incubator`: makespan 60900s vs gold 76260s; critical path overlap 0.40
