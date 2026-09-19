# eval-prompts results

Generated: 2026-09-19T19:57:00+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-wedding-reception-timeline | 1.00/1.00/1.00 | 1.00 | 0.33/0.29 | 0.00 | 0.48/0.63/0.55 | 0.96 | 0.00 | 0.05 |
| **mean (n=1)** | **1.00/1.00/1.00** | **1.00** | **0.33/0.29** | **0.00** | **0.48/0.63/0.55** | **0.96** | **0.00** | **0.05** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `event-wedding-reception-timeline`: makespan 20100s vs gold 23400s; critical path overlap 0.40
