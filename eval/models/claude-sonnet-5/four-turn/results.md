# eval-prompts results

Generated: 2026-09-19T03:28:47+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/1.00/1.00 | 1.00 | 0.67/0.67 | 0.00 | 0.68/0.75/0.71 | 0.57 | 1.00 | 0.05 |
| event-product-launch-run-of-show | 0.94/0.94/0.94 | 0.88 | 0.20/0.17 | 0.00 | 0.50/0.61/0.55 | 0.98 | 1.00 | 0.05 |
| fitness-hiit-circuit-intervals | 1.00/0.85/0.92 | 1.00 | 1.00/1.00 | 1.00 | 0.41/0.27/0.32 | 0.64 | 0.00 | 0.04 |
| fitness-partner-upper-body-supersets | 0.64/0.64/0.64 | 0.89 | 0.29/0.40 | 1.00 | 0.28/0.29/0.28 | 0.71 | 1.00 | 0.03 |
| kitchen-backyard-barbecue-smoker-grill | 0.95/1.00/0.97 | 0.94 | 0.67/0.67 | 1.00 | 0.73/0.84/0.78 | 1.00 | 1.00 | 0.05 |
| kitchen-country-loaf-bread-bake (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-cell-passaging-hood-incubator | 0.91/0.95/0.93 | 0.90 | 0.83/0.83 | 1.00 | 0.59/0.73/0.66 | 1.00 | 0.00 | 0.04 |
| **mean (n=7)** | **0.78/0.77/0.77** | **0.80** | **0.52/0.53** | **0.57** | **0.46/0.50/0.47** | **0.70** | **0.57** | **0.04** |

JS validator: ran on 6/7 programs

Missing predictions (scored zero): kitchen-country-loaf-bread-bake

## End-to-end failures

- `fitness-hiit-circuit-intervals`: critical path overlap 0.22
- `lab-cell-passaging-hood-incubator`: makespan 61500s vs gold 76260s
