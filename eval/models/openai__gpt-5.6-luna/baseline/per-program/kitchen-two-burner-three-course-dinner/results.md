# eval-prompts results

Generated: 2026-09-19T19:28:20+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-two-burner-three-course-dinner | 1.00/0.25/0.40 | 1.00 | 0.43/0.50 | 1.00 | 0.00/0.00/0.00 | 0.80 | 0.00 | 0.75 |
| **mean (n=1)** | **1.00/0.25/0.40** | **1.00** | **0.43/0.50** | **1.00** | **0.00/0.00/0.00** | **0.80** | **0.00** | **0.75** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-two-burner-three-course-dinner`: makespan 30300s vs gold 22500s; critical path overlap 0.15
