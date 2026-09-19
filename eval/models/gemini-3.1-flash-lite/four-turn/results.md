# eval-prompts results

Generated: 2026-09-19T17:19:20+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/1.00/1.00 | 1.00 | 0.80/0.67 | 0.00 | 0.65/0.65/0.65 | 0.94 | 1.00 | 0.00 |
| event-product-launch-run-of-show | 0.93/0.78/0.85 | 1.00 | 0.20/0.17 | 0.00 | 0.53/0.44/0.48 | 0.91 | 0.00 | 0.00 |
| event-theater-load-in-soundcheck (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| event-wedding-reception-timeline | 1.00/1.00/1.00 | 1.00 | 0.40/0.29 | 0.00 | 0.68/0.68/0.68 | 0.82 | 1.00 | 0.05 |
| fitness-hiit-circuit-intervals | 0.33/0.07/0.12 | 1.00 | 1.00/1.00 | 1.00 | 0.17/0.02/0.04 | 1.00 | 0.00 | 0.33 |
| fitness-partner-upper-body-supersets | 1.00/0.36/0.53 | 1.00 | 1.00/0.80 | 1.00 | 0.90/0.24/0.38 | 0.80 | 0.00 | 0.00 |
| fitness-rowing-erg-interval-session | 0.86/0.21/0.34 | 1.00 | 0.50/0.67 | 1.00 | 0.29/0.07/0.11 | 0.73 | 0.00 | 0.42 |
| fitness-swim-practice-lane-assignments | 0.89/0.40/0.55 | 0.62 | 0.33/0.25 | 0.00 | 0.22/0.09/0.13 | 1.00 | 1.00 | 0.44 |
| kitchen-backyard-barbecue-smoker-grill | 1.00/0.89/0.94 | 0.81 | 0.40/0.33 | 1.00 | 0.56/0.47/0.51 | 0.70 | 0.00 | 0.00 |
| kitchen-country-loaf-bread-bake | 1.00/0.75/0.86 | 0.89 | 0.33/0.50 | 1.00 | 0.50/0.35/0.41 | 0.65 | 0.00 | 0.00 |
| kitchen-griddle-breakfast-for-six | 0.92/0.63/0.75 | 0.75 | 0.60/0.50 | 1.00 | 0.71/0.43/0.54 | 0.91 | 1.00 | 0.00 |
| kitchen-holiday-cookie-batch | 1.00/0.95/0.97 | 0.95 | 0.50/0.50 | 1.00 | 0.62/0.50/0.55 | 0.48 | 0.00 | 0.00 |
| kitchen-sheet-pan-chicken-dinner | 0.93/0.93/0.93 | 0.92 | 0.67/0.67 | 1.00 | 0.50/0.39/0.44 | 0.81 | 1.00 | 0.00 |
| kitchen-soup-and-salad-lunch | 1.00/0.93/0.97 | 0.93 | 0.40/0.50 | 1.00 | 0.75/0.71/0.73 | 0.91 | 1.00 | 0.00 |
| lab-cell-passaging-hood-incubator | 1.00/0.90/0.95 | 0.95 | 0.67/0.67 | 1.00 | 0.95/0.73/0.83 | 0.55 | 0.00 | 0.00 |
| lab-elisa-plate-wash | 1.00/0.91/0.95 | 1.00 | 0.50/0.40 | 1.00 | 0.85/0.68/0.76 | 1.00 | 0.00 | 0.00 |
| lab-microbiology-streak-and-incubate | 0.88/0.39/0.54 | 0.57 | 0.50/0.40 | 1.00 | 0.75/0.32/0.44 | 0.52 | 0.00 | 0.00 |
| lab-pcr-and-gel | 0.94/1.00/0.97 | 1.00 | 1.00/0.86 | 1.00 | 0.72/0.72/0.72 | 0.66 | 1.00 | 0.00 |
| lab-plasmid-miniprep-digest | 1.00/0.91/0.95 | 0.90 | 0.86/0.67 | 1.00 | 0.75/0.62/0.68 | 0.72 | 1.00 | 0.05 |
| lab-western-blot-transfer-block | 1.00/1.00/1.00 | 1.00 | 1.00/1.00 | 1.00 | 0.76/0.70/0.73 | 0.66 | 0.00 | 0.00 |
| **mean (n=20)** | **0.88/0.70/0.76** | **0.86** | **0.58/0.54** | **0.75** | **0.59/0.44/0.49** | **0.74** | **0.40** | **0.06** |

JS validator: ran on 19/20 programs

Missing predictions (scored zero): event-theater-load-in-soundcheck

## End-to-end failures

- `event-product-launch-run-of-show`: makespan 7320s vs gold 13020s
- `fitness-hiit-circuit-intervals`: critical path overlap 0.22
- `fitness-partner-upper-body-supersets`: makespan 650s vs gold 1405s; critical path overlap 0.36
- `fitness-rowing-erg-interval-session`: critical path overlap 0.18
- `kitchen-backyard-barbecue-smoker-grill`: makespan 54540s vs gold 43320s
- `kitchen-country-loaf-bread-bake`: makespan 98940s vs gold 88560s
- `kitchen-holiday-cookie-batch`: makespan 17820s vs gold 14220s
- `lab-cell-passaging-hood-incubator`: makespan 6300s vs gold 76260s
- `lab-elisa-plate-wash`: makespan 22200s vs gold 76200s
- `lab-microbiology-streak-and-incubate`: makespan 118200s vs gold 98400s; critical path overlap 0.44
- `lab-western-blot-transfer-block`: makespan 68220s vs gold 78120s
