# eval-prompts results

Generated: 2026-09-19T20:00:01+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-two-burner-three-course-dinner | 0.83/0.75/0.79 | 1.00 | 0.60/0.50 | 1.00 | 0.50/0.43/0.46 | 0.81 | 0.00 | 0.00 |
| **mean (n=1)** | **0.83/0.75/0.79** | **1.00** | **0.60/0.50** | **1.00** | **0.50/0.43/0.46** | **0.81** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-two-burner-three-course-dinner`: makespan 18600s vs gold 22500s; critical path overlap 0.38
