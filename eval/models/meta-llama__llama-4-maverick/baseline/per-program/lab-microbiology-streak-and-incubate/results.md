# eval-prompts results

Generated: 2026-09-19T19:37:52+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-microbiology-streak-and-incubate | 1.00/0.33/0.50 | 1.00 | 0.38/0.60 | 1.00 | 0.50/0.16/0.24 | 0.60 | 0.00 | 0.50 |
| **mean (n=1)** | **1.00/0.33/0.50** | **1.00** | **0.38/0.60** | **1.00** | **0.50/0.16/0.24** | **0.60** | **0.00** | **0.50** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-microbiology-streak-and-incubate`: js validator: Step "supervisor-signoff" has no duration.; critical path overlap 0.33
