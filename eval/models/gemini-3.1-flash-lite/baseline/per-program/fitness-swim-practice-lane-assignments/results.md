# eval-prompts results

Generated: 2026-09-19T17:17:02+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-swim-practice-lane-assignments | 1.00/0.25/0.40 | 1.00 | 0.67/0.50 | 0.00 | 0.40/0.09/0.15 | 1.00 | 0.00 | 0.55 |
| **mean (n=1)** | **1.00/0.25/0.40** | **1.00** | **0.67/0.50** | **0.00** | **0.40/0.09/0.15** | **1.00** | **0.00** | **0.55** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-swim-practice-lane-assignments`: makespan 7800s vs gold 8700s; critical path overlap 0.40
