# eval-prompts results

Generated: 2026-09-19T17:40:35+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-wedding-reception-timeline | 1.00/0.32/0.48 | 1.00 | 0.57/0.57 | 0.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.68 |
| **mean (n=1)** | **1.00/0.32/0.48** | **1.00** | **0.57/0.57** | **0.00** | **0.00/0.00/0.00** | **1.00** | **0.00** | **0.68** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `event-wedding-reception-timeline`: makespan 19800s vs gold 23400s; critical path overlap 0.33
