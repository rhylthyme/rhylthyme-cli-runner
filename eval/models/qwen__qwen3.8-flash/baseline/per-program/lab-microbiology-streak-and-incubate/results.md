# eval-prompts results

Generated: 2026-09-19T19:55:34+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-microbiology-streak-and-incubate | 1.00/0.22/0.36 | 1.00 | 0.50/0.60 | 1.00 | 0.50/0.11/0.17 | 0.50 | 0.00 | 0.73 |
| **mean (n=1)** | **1.00/0.22/0.36** | **1.00** | **0.50/0.60** | **1.00** | **0.50/0.11/0.17** | **0.50** | **0.00** | **0.73** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-microbiology-streak-and-incubate`: makespan 122100s vs gold 98400s; critical path overlap 0.11
