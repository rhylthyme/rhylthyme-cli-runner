# eval-prompts results

Generated: 2026-09-19T19:46:45+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-pcr-and-gel | 0.94/1.00/0.97 | 0.94 | 0.83/0.71 | 1.00 | 0.78/0.78/0.78 | 0.87 | 0.00 | 0.00 |
| **mean (n=1)** | **0.94/1.00/0.97** | **0.94** | **0.83/0.71** | **1.00** | **0.78/0.78/0.78** | **0.87** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-pcr-and-gel`: makespan 10620s vs gold 12660s
