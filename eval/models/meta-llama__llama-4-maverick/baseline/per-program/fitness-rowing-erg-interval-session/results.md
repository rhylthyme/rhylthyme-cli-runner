# eval-prompts results

Generated: 2026-09-19T19:36:28+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-rowing-erg-interval-session | 1.00/0.21/0.35 | 0.83 | 0.33/0.33 | 0.00 | 0.33/0.07/0.11 | 0.93 | 0.00 | 0.65 |
| **mean (n=1)** | **1.00/0.21/0.35** | **0.83** | **0.33/0.33** | **0.00** | **0.33/0.07/0.11** | **0.93** | **0.00** | **0.65** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-rowing-erg-interval-session`: makespan 5160s vs gold 4560s; critical path overlap 0.27
