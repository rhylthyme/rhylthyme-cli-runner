# eval-prompts results

Generated: 2026-09-19T03:28:48+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/0.55/0.71 | 1.00 | 0.80/0.67 | 0.00 | 0.50/0.30/0.37 | 0.96 | 1.00 | 0.45 |
| event-product-launch-run-of-show | 1.00/0.56/0.71 | 0.90 | 0.25/0.17 | 1.00 | 0.20/0.11/0.14 | 0.98 | 1.00 | 0.44 |
| fitness-hiit-circuit-intervals | 1.00/0.07/0.14 | 1.00 | 1.00/1.00 | 1.00 | 0.25/0.02/0.04 | 0.00 | 0.00 | 0.92 |
| fitness-partner-upper-body-supersets | 1.00/0.39/0.56 | 1.00 | 0.29/0.40 | 1.00 | 0.33/0.18/0.24 | 1.00 | 0.00 | 0.59 |
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.83/0.91 | 1.00 | 0.33/0.33 | 1.00 | 0.56/0.53/0.54 | 1.00 | 1.00 | 0.17 |
| kitchen-country-loaf-bread-bake | 1.00/0.50/0.67 | 1.00 | 0.67/1.00 | 1.00 | 0.58/0.27/0.37 | 0.73 | 0.00 | 0.50 |
| lab-cell-passaging-hood-incubator | 1.00/0.24/0.38 | 1.00 | 0.80/0.67 | 1.00 | 0.60/0.12/0.19 | 1.00 | 0.00 | 0.58 |
| **mean (n=7)** | **1.00/0.45/0.58** | **0.99** | **0.59/0.60** | **0.86** | **0.43/0.22/0.27** | **0.81** | **0.43** | **0.52** |

JS validator: ran on 7/7 programs

## End-to-end failures

- `fitness-hiit-circuit-intervals`: critical path overlap 0.22
- `fitness-partner-upper-body-supersets`: critical path overlap 0.43
- `kitchen-country-loaf-bread-bake`: critical path overlap 0.38
- `lab-cell-passaging-hood-incubator`: makespan 60900s vs gold 76260s; critical path overlap 0.40
