# eval-prompts results

Generated: 2026-09-19T17:14:50+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| lab-elisa-plate-wash | 1.00/0.05/0.09 | 1.00 | 0.25/0.20 | 1.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.91 |
| **mean (n=1)** | **1.00/0.05/0.09** | **1.00** | **0.25/0.20** | **1.00** | **0.00/0.00/0.00** | **1.00** | **0.00** | **0.91** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `lab-elisa-plate-wash`: makespan 20400s vs gold 76200s; critical path overlap 0.00
