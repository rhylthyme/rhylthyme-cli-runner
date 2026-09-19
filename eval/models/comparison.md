# Model x prompt comparison

One run per cell. Each table covers only the programs that every model in it ran, so its means are like for like. A run that produced no program counts as an end-to-end failure; its component scores are left out. Costs are list-price estimates (DeepSeek at peak rates; it actually charged about a third of that off-peak).

Programs run per model: haiku-4-5 24, sonnet-5 7, deepseek-flash 16, gemini-3.1-flash-lite 20.

## 7 programs: haiku-4-5, sonnet-5, deepseek-flash, gemini-3.1-flash-lite

Domains: event 2, fitness 2, kitchen 2, lab 1.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | sonnet-5 baseline | sonnet-5 four-turn | deepseek-flash baseline | deepseek-flash four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn |
|---|---|---|---|---|---|---|---|---|
| Steps F1 | 0.56 | 0.91 | 0.58 | 0.90 | 0.36 | 0.93 | 0.48 | 0.75 |
| Durations accuracy | 0.99 | 0.92 | 0.99 | 0.94 | 1.00 | 0.93 | 0.90 | 0.95 |
| Relationships F1 | 0.30 | 0.64 | 0.27 | 0.55 | 0.13 | 0.54 | 0.26 | 0.47 |
| Resources recall | 0.60 | 0.72 | 0.60 | 0.62 | 0.63 | 0.72 | 0.46 | 0.59 |
| Track structure (Rand) | 0.89 | 0.91 | 0.81 | 0.81 | 1.00 | 0.87 | 0.84 | 0.79 |
| Unsupported steps | 60% | 2% | 52% | 4% | 75% | 5% | 50% | 5% |
| End-to-end pass | 29% | 43% | 43% | 57% | 14% | 43% | 0% | 14% |
| Produced a program | 100% | 100% | 100% | 86% | 71% | 71% | 100% | 100% |
| Cost per program (USD) | $0.046 | $0.091 | $0.255 | $0.508 | $0.047 | $0.081 | $0.006 | $0.018 |
| Output tokens per program | 6,492 | 10,683 | 22,573 | 39,553 | 36,565 | 55,536 | 2,214 | 6,132 |
| Validator fix rounds | 0.86 | 0.43 | 1.00 | 0.86 | 1.57 | 1.71 | 0.71 | 0.71 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | sonnet-5 | deepseek-flash | gemini-3.1-flash-lite |
|---|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass | pass |
| event-product-launch-run-of-show | fail | pass | fail | fail |
| fitness-hiit-circuit-intervals | pass | fail | pass | fail |
| fitness-partner-upper-body-supersets | fail | pass | pass | fail |
| kitchen-backyard-barbecue-smoker-grill | pass | pass | fail | fail |
| kitchen-country-loaf-bread-bake | fail | no program | no program | fail |
| lab-cell-passaging-hood-incubator | fail | fail | no program | fail |

## 16 programs: haiku-4-5, deepseek-flash, gemini-3.1-flash-lite

Domains: event 4, fitness 4, kitchen 4, lab 4.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | deepseek-flash baseline | deepseek-flash four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn |
|---|---|---|---|---|---|---|
| Steps F1 | 0.50 | 0.92 | 0.39 | 0.88 | 0.52 | 0.75 |
| Durations accuracy | 0.86 | 0.93 | 0.90 | 0.96 | 0.94 | 0.90 |
| Relationships F1 | 0.25 | 0.63 | 0.14 | 0.57 | 0.27 | 0.48 |
| Resources recall | 0.55 | 0.53 | 0.60 | 0.66 | 0.47 | 0.53 |
| Track structure (Rand) | 0.80 | 0.92 | 0.87 | 0.89 | 0.83 | 0.78 |
| Unsupported steps | 61% | 1% | 72% | 5% | 47% | 8% |
| End-to-end pass | 12% | 56% | 19% | 44% | 12% | 31% |
| Produced a program | 100% | 100% | 62% | 62% | 100% | 94% |
| Cost per program (USD) | $0.044 | $0.088 | $0.047 | $0.079 | $0.006 | $0.019 |
| Output tokens per program | 6,003 | 10,063 | 36,560 | 53,268 | 2,407 | 6,636 |
| Validator fix rounds | 1.00 | 0.44 | 1.56 | 1.56 | 0.81 | 0.88 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | deepseek-flash | gemini-3.1-flash-lite |
|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass |
| event-product-launch-run-of-show | fail | fail | fail |
| event-theater-load-in-soundcheck | fail | pass | no program |
| event-wedding-reception-timeline | pass | fail | pass |
| fitness-hiit-circuit-intervals | pass | pass | fail |
| fitness-partner-upper-body-supersets | fail | pass | fail |
| fitness-rowing-erg-interval-session | pass | pass | fail |
| fitness-swim-practice-lane-assignments | pass | pass | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | fail | fail |
| kitchen-country-loaf-bread-bake | fail | no program | fail |
| kitchen-griddle-breakfast-for-six | pass | no program | pass |
| kitchen-holiday-cookie-batch | fail | no program | fail |
| lab-cell-passaging-hood-incubator | fail | no program | fail |
| lab-elisa-plate-wash | fail | no program | fail |
| lab-microbiology-streak-and-incubate | pass | no program | fail |
| lab-pcr-and-gel | pass | pass | pass |

## 20 programs: haiku-4-5, gemini-3.1-flash-lite

Domains: event 4, fitness 4, kitchen 6, lab 6.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn |
|---|---|---|---|---|
| Steps F1 | 0.50 | 0.92 | 0.53 | 0.80 |
| Durations accuracy | 0.88 | 0.92 | 0.95 | 0.91 |
| Relationships F1 | 0.23 | 0.62 | 0.26 | 0.52 |
| Resources recall | 0.59 | 0.56 | 0.51 | 0.57 |
| Track structure (Rand) | 0.83 | 0.92 | 0.82 | 0.78 |
| Unsupported steps | 63% | 1% | 48% | 7% |
| End-to-end pass | 10% | 65% | 15% | 40% |
| Produced a program | 100% | 100% | 95% | 95% |
| Cost per program (USD) | $0.046 | $0.091 | $0.007 | $0.019 |
| Output tokens per program | 6,211 | 10,296 | 2,760 | 6,545 |
| Validator fix rounds | 1.05 | 0.55 | 1.00 | 0.80 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | gemini-3.1-flash-lite |
|---|---|---|
| event-conference-session-av-checks | pass | pass |
| event-product-launch-run-of-show | fail | fail |
| event-theater-load-in-soundcheck | fail | no program |
| event-wedding-reception-timeline | pass | pass |
| fitness-hiit-circuit-intervals | pass | fail |
| fitness-partner-upper-body-supersets | fail | fail |
| fitness-rowing-erg-interval-session | pass | fail |
| fitness-swim-practice-lane-assignments | pass | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | fail |
| kitchen-country-loaf-bread-bake | fail | fail |
| kitchen-griddle-breakfast-for-six | pass | pass |
| kitchen-holiday-cookie-batch | fail | fail |
| kitchen-sheet-pan-chicken-dinner | pass | pass |
| kitchen-soup-and-salad-lunch | pass | pass |
| lab-cell-passaging-hood-incubator | fail | fail |
| lab-elisa-plate-wash | fail | fail |
| lab-microbiology-streak-and-incubate | pass | fail |
| lab-pcr-and-gel | pass | pass |
| lab-plasmid-miniprep-digest | pass | pass |
| lab-western-blot-transfer-block | pass | fail |
