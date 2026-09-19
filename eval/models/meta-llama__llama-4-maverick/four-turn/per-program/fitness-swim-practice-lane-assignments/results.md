# eval-prompts results

Generated: 2026-09-19T19:47:46+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-swim-practice-lane-assignments | 0.75/0.45/0.56 | 1.00 | 0.00/0.00 | 0.00 | 0.17/0.09/0.12 | 0.89 | 0.00 | 0.00 |
| **mean (n=1)** | **0.75/0.45/0.56** | **1.00** | **0.00/0.00** | **0.00** | **0.17/0.09/0.12** | **0.89** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-swim-practice-lane-assignments`: makespan 9600s vs gold 8700s; critical path overlap 0.20
