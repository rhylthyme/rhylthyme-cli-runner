# eval-prompts results

Generated: 2026-09-19T20:04:46+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| kitchen-two-burner-three-course-dinner | 1.00/0.60/0.75 | 0.83 | 0.33/0.17 | 1.00 | 0.42/0.24/0.30 | 0.83 | 0.00 | 0.43 |
| **mean (n=1)** | **1.00/0.60/0.75** | **0.83** | **0.33/0.17** | **1.00** | **0.42/0.24/0.30** | **0.83** | **0.00** | **0.43** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `kitchen-two-burner-three-course-dinner`: makespan 29400s vs gold 22500s; critical path overlap 0.23
