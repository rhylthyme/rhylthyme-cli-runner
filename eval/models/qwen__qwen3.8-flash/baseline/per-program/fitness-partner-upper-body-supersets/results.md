# eval-prompts results

Generated: 2026-09-19T19:27:01+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-partner-upper-body-supersets | 1.00/0.07/0.13 | 1.00 | 0.43/0.60 | 1.00 | 1.00/0.05/0.10 | 1.00 | 0.00 | 0.86 |
| **mean (n=1)** | **1.00/0.07/0.13** | **1.00** | **0.43/0.60** | **1.00** | **1.00/0.05/0.10** | **1.00** | **0.00** | **0.86** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-partner-upper-body-supersets`: makespan 1040s vs gold 1405s; critical path overlap 0.14
