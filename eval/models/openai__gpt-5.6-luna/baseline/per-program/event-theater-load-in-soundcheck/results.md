# eval-prompts results

Generated: 2026-09-19T19:18:07+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-theater-load-in-soundcheck | 1.00/0.70/0.82 | 1.00 | 0.50/0.57 | 1.00 | 0.59/0.45/0.51 | 0.89 | 0.00 | 0.26 |
| **mean (n=1)** | **1.00/0.70/0.82** | **1.00** | **0.50/0.57** | **1.00** | **0.59/0.45/0.51** | **0.89** | **0.00** | **0.26** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `event-theater-load-in-soundcheck`: makespan 35100s vs gold 28200s
