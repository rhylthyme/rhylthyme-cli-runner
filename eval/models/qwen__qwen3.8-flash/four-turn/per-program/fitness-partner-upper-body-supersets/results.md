# eval-prompts results

Generated: 2026-09-19T19:39:39+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-partner-upper-body-supersets | 1.00/0.46/0.63 | 1.00 | 0.40/0.40 | 1.00 | 0.53/0.21/0.30 | 0.46 | 0.00 | 0.00 |
| **mean (n=1)** | **1.00/0.46/0.63** | **1.00** | **0.40/0.40** | **1.00** | **0.53/0.21/0.30** | **0.46** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-partner-upper-body-supersets`: js validator: Track "Dumbbells - Partner A overhead press (1 of 2)": "Partner B overhead press after swap (1 of 2)" (ends 910s) overlaps "Partner A pull-ups after swap (1 of 2)" (starts 865s) by 45s.; Track "Dumbbells - Partner A overhead press (2 of 2)": "Partner B overhead press after swap (2 of 2)" (ends 910s) overlaps "Partner A pull-ups after swap (2 of 2)" (starts 865s) by 45s.; makespan 1160s vs gold 1405s
