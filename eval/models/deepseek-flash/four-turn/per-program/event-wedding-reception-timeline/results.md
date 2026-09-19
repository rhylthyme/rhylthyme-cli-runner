# eval-prompts results

Generated: 2026-09-19T17:41:38+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-wedding-reception-timeline | 1.00/1.00/1.00 | 1.00 | 0.67/0.57 | 0.00 | 0.65/0.68/0.67 | 0.90 | 0.00 | 0.10 |
| **mean (n=1)** | **1.00/1.00/1.00** | **1.00** | **0.67/0.57** | **0.00** | **0.65/0.68/0.67** | **0.90** | **0.00** | **0.10** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `event-wedding-reception-timeline`: makespan 19500s vs gold 23400s; critical path overlap 0.40
