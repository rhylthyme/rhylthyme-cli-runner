# eval-prompts results

Generated: 2026-09-19T17:19:21+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/0.25/0.40 | 1.00 | 0.80/0.67 | 0.00 | 0.60/0.15/0.24 | 0.70 | 0.00 | 0.64 |
| event-product-launch-run-of-show | 1.00/0.39/0.56 | 1.00 | 0.25/0.17 | 0.00 | 0.57/0.22/0.32 | 0.71 | 0.00 | 0.59 |
| event-theater-load-in-soundcheck | 1.00/0.65/0.79 | 1.00 | 0.71/0.71 | 1.00 | 0.54/0.32/0.40 | 0.87 | 1.00 | 0.19 |
| event-wedding-reception-timeline | 1.00/1.00/1.00 | 0.89 | 0.33/0.29 | 0.00 | 0.58/0.58/0.58 | 0.63 | 0.00 | 0.00 |
| fitness-hiit-circuit-intervals | 1.00/0.07/0.14 | 1.00 | 0.50/0.20 | 1.00 | 0.50/0.02/0.05 | 1.00 | 0.00 | 0.60 |
| fitness-partner-upper-body-supersets | 1.00/0.54/0.70 | 1.00 | 0.60/0.60 | 1.00 | 0.40/0.16/0.23 | 1.00 | 0.00 | 0.42 |
| fitness-rowing-erg-interval-session | 1.00/0.18/0.30 | 0.80 | 0.50/0.33 | 0.00 | 0.40/0.07/0.12 | 0.80 | 0.00 | 0.67 |
| fitness-swim-practice-lane-assignments | 1.00/0.25/0.40 | 1.00 | 0.67/0.50 | 0.00 | 0.40/0.09/0.15 | 1.00 | 0.00 | 0.55 |
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.67/0.80 | 0.75 | 0.33/0.33 | 1.00 | 0.75/0.47/0.58 | 0.91 | 0.00 | 0.25 |
| kitchen-country-loaf-bread-bake | 1.00/0.29/0.45 | 0.57 | 0.60/0.75 | 1.00 | 0.43/0.12/0.18 | 0.52 | 0.00 | 0.42 |
| kitchen-griddle-breakfast-for-six | 1.00/0.42/0.59 | 1.00 | 0.50/0.33 | 1.00 | 0.50/0.17/0.26 | 1.00 | 0.00 | 0.43 |
| kitchen-holiday-cookie-batch | 1.00/0.45/0.62 | 1.00 | 0.60/0.50 | 1.00 | 0.44/0.15/0.23 | 0.64 | 0.00 | 0.36 |
| kitchen-sheet-pan-chicken-dinner | 1.00/0.43/0.60 | 1.00 | 0.67/0.67 | 1.00 | 0.50/0.17/0.25 | 0.93 | 1.00 | 0.54 |
| kitchen-soup-and-salad-lunch | 1.00/0.40/0.57 | 1.00 | 0.50/0.50 | 1.00 | 0.33/0.12/0.17 | 0.73 | 0.00 | 0.54 |
| lab-cell-passaging-hood-incubator | 1.00/0.19/0.32 | 1.00 | 0.75/0.50 | 1.00 | 0.75/0.12/0.20 | 1.00 | 0.00 | 0.60 |
| lab-elisa-plate-wash | 1.00/0.05/0.09 | 1.00 | 0.25/0.20 | 1.00 | 0.00/0.00/0.00 | 1.00 | 0.00 | 0.91 |
| lab-microbiology-streak-and-incubate | 1.00/0.28/0.43 | 1.00 | 0.60/0.60 | 1.00 | 0.60/0.16/0.25 | 0.80 | 0.00 | 0.55 |
| lab-pcr-and-gel | 1.00/0.62/0.77 | 1.00 | 1.00/0.86 | 1.00 | 0.64/0.39/0.48 | 0.64 | 1.00 | 0.38 |
| lab-plasmid-miniprep-digest | 1.00/0.36/0.53 | 1.00 | 1.00/1.00 | 1.00 | 0.38/0.12/0.19 | 0.64 | 0.00 | 0.56 |
| lab-western-blot-transfer-block (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| **mean (n=20)** | **0.95/0.37/0.50** | **0.90** | **0.56/0.49** | **0.70** | **0.47/0.18/0.24** | **0.78** | **0.15** | **0.46** |

JS validator: ran on 19/20 programs

Missing predictions (scored zero): lab-western-blot-transfer-block

## End-to-end failures

- `event-conference-session-av-checks`: makespan 7920s vs gold 15240s; critical path overlap 0.06
- `event-product-launch-run-of-show`: critical path overlap 0.25
- `event-wedding-reception-timeline`: makespan 27300s vs gold 23400s
- `fitness-hiit-circuit-intervals`: makespan 1020s vs gold 1320s; critical path overlap 0.22
- `fitness-partner-upper-body-supersets`: critical path overlap 0.43
- `fitness-rowing-erg-interval-session`: critical path overlap 0.27
- `fitness-swim-practice-lane-assignments`: makespan 7800s vs gold 8700s; critical path overlap 0.40
- `kitchen-backyard-barbecue-smoker-grill`: makespan 57780s vs gold 43320s; critical path overlap 0.45
- `kitchen-country-loaf-bread-bake`: critical path overlap 0.31
- `kitchen-griddle-breakfast-for-six`: makespan 3120s vs gold 3840s; critical path overlap 0.12
- `kitchen-holiday-cookie-batch`: makespan 16920s vs gold 14220s
- `kitchen-soup-and-salad-lunch`: makespan 5640s vs gold 4080s; critical path overlap 0.14
- `lab-cell-passaging-hood-incubator`: makespan 5120s vs gold 76260s; critical path overlap 0.30
- `lab-elisa-plate-wash`: makespan 20400s vs gold 76200s; critical path overlap 0.00
- `lab-microbiology-streak-and-incubate`: critical path overlap 0.44
- `lab-plasmid-miniprep-digest`: critical path overlap 0.44
