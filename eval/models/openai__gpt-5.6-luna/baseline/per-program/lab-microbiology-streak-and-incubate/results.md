# eval-prompts results

Generated: 2026-09-19T19:23:38+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-microbiology-streak-and-incubate | 1.00/0.28/0.43 | 1.00 | 0.38/0.60 | 1.00 | 0.20/0.05/0.08 | 0.60 | 0.00 | 0.67 |
| **mean (n=1)** | **1.00/0.28/0.43** | **1.00** | **0.38/0.60** | **1.00** | **0.20/0.05/0.08** | **0.60** | **0.00** | **0.67** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-microbiology-streak-and-incubate`: makespan 115200s vs gold 98400s; critical path overlap 0.33
