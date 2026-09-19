# Model x prompt comparison

Programs scored in every cell: 7 (event 2, fitness 2, kitchen 2, lab 1). One run per cell; means over those programs only. A run that produced no program counts as an end-to-end failure; its component scores are left out.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | sonnet-5 baseline | sonnet-5 four-turn |
|---|---|---|---|---|
| Steps F1 | 0.56 | 0.91 | 0.58 | 0.90 |
| Durations accuracy | 0.99 | 0.92 | 0.99 | 0.94 |
| Relationships F1 | 0.30 | 0.64 | 0.27 | 0.55 |
| Resources recall | 0.60 | 0.72 | 0.60 | 0.62 |
| Track structure (Rand) | 0.89 | 0.91 | 0.81 | 0.81 |
| Unsupported steps | 60% | 2% | 52% | 4% |
| End-to-end pass | 29% | 43% | 43% | 57% |
| Produced a program | 100% | 100% | 100% | 86% |
| Cost per program (USD) | $0.046 | $0.091 | $0.255 | $0.508 |
| Output tokens per program | 6,492 | 10,683 | 22,573 | 39,553 |
| Validator fix rounds | 0.86 | 0.43 | 1.00 | 0.86 |

## End-to-end pass by program (four-turn)

| Program | haiku-4-5 | sonnet-5 |
|---|---|---|
| event-conference-session-av-checks | pass | pass |
| event-product-launch-run-of-show | fail | pass |
| fitness-hiit-circuit-intervals | pass | fail |
| fitness-partner-upper-body-supersets | fail | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | pass |
| kitchen-country-loaf-bread-bake | fail | no program |
| lab-cell-passaging-hood-incubator | fail | fail |
