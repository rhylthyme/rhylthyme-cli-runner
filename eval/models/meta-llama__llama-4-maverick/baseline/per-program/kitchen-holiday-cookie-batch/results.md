# eval-prompts results

Generated: 2026-09-19T19:47:58+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-holiday-cookie-batch | 1.00/0.40/0.57 | 1.00 | 0.60/0.50 | 1.00 | 0.38/0.12/0.18 | 0.50 | 0.00 | 0.58 |
| **mean (n=1)** | **1.00/0.40/0.57** | **1.00** | **0.60/0.50** | **1.00** | **0.38/0.12/0.18** | **0.50** | **0.00** | **0.58** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-holiday-cookie-batch`: makespan 17820s vs gold 14220s; critical path overlap 0.44
