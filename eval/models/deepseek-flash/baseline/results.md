# eval-prompts results

Generated: 2026-09-19T17:51:22+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/0.10/0.18 | 1.00 | 0.60/0.50 | 0.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.90 |
| event-product-launch-run-of-show | 1.00/0.39/0.56 | 1.00 | 0.43/0.50 | 0.00 | 0.29/0.11/0.16 | 1.00 | 1.00 | 0.63 |
| event-theater-load-in-soundcheck | 1.00/0.55/0.71 | 1.00 | 0.57/0.57 | 1.00 | 0.67/0.36/0.47 | 0.96 | 1.00 | 0.42 |
| event-wedding-reception-timeline | 1.00/0.32/0.48 | 1.00 | 0.57/0.57 | 0.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.68 |
| fitness-hiit-circuit-intervals | 1.00/0.22/0.36 | 1.00 | 1.00/1.00 | 1.00 | 0.25/0.07/0.11 | 1.00 | 0.00 | 0.78 |
| fitness-partner-upper-body-supersets (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| fitness-rowing-erg-interval-session (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| fitness-swim-practice-lane-assignments | 1.00/0.15/0.26 | 1.00 | 0.67/0.50 | 0.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.83 |
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.22/0.36 | 1.00 | 0.33/0.33 | 1.00 | 0.50/0.11/0.17 | 1.00 | 0.00 | 0.78 |
| kitchen-country-loaf-bread-bake (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| kitchen-griddle-breakfast-for-six (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| kitchen-holiday-cookie-batch (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-cell-passaging-hood-incubator | 1.00/0.19/0.32 | 1.00 | 1.00/0.83 | 1.00 | 0.75/0.12/0.20 | 1.00 | 0.00 | 0.67 |
| lab-elisa-plate-wash | 0.00/0.00/0.00 | 0.00 | 0.20/0.20 | 1.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 1.00 |
| lab-microbiology-streak-and-incubate (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-pcr-and-gel | 1.00/0.50/0.67 | 1.00 | 0.78/1.00 | 1.00 | 0.50/0.22/0.31 | 0.79 | 1.00 | 0.50 |
| **mean (n=16)** | **0.56/0.16/0.24** | **0.56** | **0.38/0.38** | **0.38** | **0.18/0.06/0.09** | **0.55** | **0.19** | **0.45** |

JS validator: ran on 10/16 programs

Missing predictions (scored zero): fitness-partner-upper-body-supersets, fitness-rowing-erg-interval-session, kitchen-country-loaf-bread-bake, kitchen-griddle-breakfast-for-six, kitchen-holiday-cookie-batch, lab-microbiology-streak-and-incubate

## End-to-end failures

- `event-conference-session-av-checks`: critical path overlap 0.11
- `event-wedding-reception-timeline`: makespan 19800s vs gold 23400s; critical path overlap 0.33
- `fitness-hiit-circuit-intervals`: critical path overlap 0.22
- `fitness-swim-practice-lane-assignments`: critical path overlap 0.10
- `kitchen-backyard-barbecue-smoker-grill`: critical path overlap 0.00
- `lab-cell-passaging-hood-incubator`: makespan 61800s vs gold 76260s; critical path overlap 0.40
- `lab-elisa-plate-wash`: critical path overlap 0.00
