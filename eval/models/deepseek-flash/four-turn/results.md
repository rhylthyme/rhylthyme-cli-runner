# eval-prompts results

Generated: 2026-09-19T17:51:21+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/1.00/1.00 | 1.00 | 0.60/0.50 | 0.00 | 0.58/0.75/0.65 | 0.86 | 1.00 | 0.05 |
| event-product-launch-run-of-show | 0.90/1.00/0.95 | 0.83 | 0.86/1.00 | 0.00 | 0.43/0.50/0.46 | 0.90 | 0.00 | 0.05 |
| event-theater-load-in-soundcheck | 1.00/0.95/0.97 | 1.00 | 0.57/0.57 | 1.00 | 0.95/0.91/0.93 | 0.88 | 1.00 | 0.05 |
| event-wedding-reception-timeline | 1.00/1.00/1.00 | 1.00 | 0.67/0.57 | 0.00 | 0.65/0.68/0.67 | 0.90 | 0.00 | 0.10 |
| fitness-hiit-circuit-intervals | 1.00/1.00/1.00 | 1.00 | 1.00/1.00 | 1.00 | 0.48/0.39/0.43 | 0.69 | 1.00 | 0.10 |
| fitness-partner-upper-body-supersets | 0.79/0.79/0.79 | 0.86 | 0.60/0.60 | 1.00 | 0.42/0.39/0.41 | 0.91 | 1.00 | 0.03 |
| fitness-rowing-erg-interval-session | 0.81/0.46/0.59 | 1.00 | 0.67/0.67 | 0.00 | 0.56/0.31/0.40 | 0.88 | 1.00 | 0.00 |
| fitness-swim-practice-lane-assignments | 0.92/0.55/0.69 | 1.00 | 0.67/0.50 | 1.00 | 0.28/0.23/0.25 | 0.95 | 1.00 | 0.08 |
| kitchen-backyard-barbecue-smoker-grill | 0.89/0.94/0.92 | 0.94 | 0.50/0.50 | 1.00 | 0.74/0.74/0.74 | 1.00 | 0.00 | 0.00 |
| kitchen-country-loaf-bread-bake (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| kitchen-griddle-breakfast-for-six (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| kitchen-holiday-cookie-batch (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-cell-passaging-hood-incubator (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-elisa-plate-wash (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-microbiology-streak-and-incubate (missing) | 0.00/0.00/0.00 | 0.00 | 0.00/0.00 | 0.00 | 0.00/0.00/0.00 | 0.00 | 0.00 | 0.00 |
| lab-pcr-and-gel | 0.84/1.00/0.91 | 0.94 | 0.62/0.71 | 1.00 | 0.67/0.78/0.72 | 0.89 | 1.00 | 0.05 |
| **mean (n=16)** | **0.57/0.54/0.55** | **0.60** | **0.42/0.41** | **0.38** | **0.36/0.36/0.35** | **0.55** | **0.44** | **0.03** |

JS validator: ran on 10/16 programs

Missing predictions (scored zero): kitchen-country-loaf-bread-bake, kitchen-griddle-breakfast-for-six, kitchen-holiday-cookie-batch, lab-cell-passaging-hood-incubator, lab-elisa-plate-wash, lab-microbiology-streak-and-incubate

## End-to-end failures

- `event-product-launch-run-of-show`: makespan 14520s vs gold 13020s
- `event-wedding-reception-timeline`: makespan 19500s vs gold 23400s; critical path overlap 0.40
- `kitchen-backyard-barbecue-smoker-grill`: critical path overlap 0.36
