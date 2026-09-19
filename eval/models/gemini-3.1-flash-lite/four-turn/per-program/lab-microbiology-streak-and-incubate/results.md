# eval-prompts results

Generated: 2026-09-19T17:16:30+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-microbiology-streak-and-incubate | 0.88/0.39/0.54 | 0.57 | 0.50/0.40 | 1.00 | 0.75/0.32/0.44 | 0.52 | 0.00 | 0.00 |
| **mean (n=1)** | **0.88/0.39/0.54** | **0.57** | **0.50/0.40** | **1.00** | **0.75/0.32/0.44** | **0.52** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-microbiology-streak-and-incubate`: makespan 118200s vs gold 98400s; critical path overlap 0.44
