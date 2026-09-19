# eval-prompts results

Generated: 2026-09-19T19:19:05+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| fitness-partner-upper-body-supersets | 1.00/0.46/0.63 | 0.38 | 0.43/0.60 | 1.00 | 0.20/0.08/0.11 | 0.42 | 0.00 | 0.00 |
| **mean (n=1)** | **1.00/0.46/0.63** | **0.38** | **0.43/0.60** | **1.00** | **0.20/0.08/0.11** | **0.42** | **0.00** | **0.00** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `fitness-partner-upper-body-supersets`: js validator: Track "Partner A - Partner A strict dumbbell overhead press set, each Superset B round (1 of 2)": "Partner A pull-up set, each Superset B round (1 of 2)" (ends 895s) overlaps "Partner B strict dumbbell overhead press set, each Superset B round (1 of 2)" (starts 865s) by 30s.; Track "Partner A - Partner A strict dumbbell overhead press set, each Superset B round (2 of 2)": "Partner A pull-up set, each Superset B round (2 of 2)" (ends 985s) overlaps "Partner B strict dumbbell overhead press set, each Superset B round (2 of 2)" (starts 955s) by 30s.; makespan 1040s vs gold 1405s; critical path overlap 0.36
