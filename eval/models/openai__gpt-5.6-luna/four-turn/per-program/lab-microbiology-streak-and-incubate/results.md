# eval-prompts results

Generated: 2026-09-19T19:33:47+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-microbiology-streak-and-incubate | 1.00/0.94/0.97 | 0.94 | 0.43/0.60 | 0.00 | 0.71/0.63/0.67 | 0.84 | 0.00 | 0.06 |
| **mean (n=1)** | **1.00/0.94/0.97** | **0.94** | **0.43/0.60** | **0.00** | **0.71/0.63/0.67** | **0.84** | **0.00** | **0.06** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-microbiology-streak-and-incubate`: makespan 113400s vs gold 98400s; critical path overlap 0.33
