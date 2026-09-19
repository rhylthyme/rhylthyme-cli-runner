# eval-prompts results

Generated: 2026-09-19T17:12:49+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-hiit-circuit-intervals | 1.00/0.07/0.14 | 1.00 | 0.50/0.20 | 1.00 | 0.50/0.02/0.05 | 1.00 | 0.00 | 0.60 |
| **mean (n=1)** | **1.00/0.07/0.14** | **1.00** | **0.50/0.20** | **1.00** | **0.50/0.02/0.05** | **1.00** | **0.00** | **0.60** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-hiit-circuit-intervals`: makespan 1020s vs gold 1320s; critical path overlap 0.22
