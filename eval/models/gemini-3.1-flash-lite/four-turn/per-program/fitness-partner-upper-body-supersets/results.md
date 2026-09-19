# eval-prompts results

Generated: 2026-09-19T17:14:23+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-partner-upper-body-supersets | 1.00/0.36/0.53 | 1.00 | 1.00/0.80 | 1.00 | 0.90/0.24/0.38 | 0.80 | 0.00 | 0.00 |
| **mean (n=1)** | **1.00/0.36/0.53** | **1.00** | **1.00/0.80** | **1.00** | **0.90/0.24/0.38** | **0.80** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-partner-upper-body-supersets`: makespan 650s vs gold 1405s; critical path overlap 0.36
