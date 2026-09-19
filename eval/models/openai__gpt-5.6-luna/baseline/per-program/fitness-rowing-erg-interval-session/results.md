# eval-prompts results

Generated: 2026-09-19T19:23:49+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-rowing-erg-interval-session | 1.00/0.11/0.19 | 1.00 | 0.50/0.67 | 0.00 | 0.50/0.07/0.12 | 0.33 | 0.00 | 0.67 |
| **mean (n=1)** | **1.00/0.11/0.19** | **1.00** | **0.50/0.67** | **0.00** | **0.50/0.07/0.12** | **0.33** | **0.00** | **0.67** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-rowing-erg-interval-session`: makespan 4080s vs gold 4560s; critical path overlap 0.27
