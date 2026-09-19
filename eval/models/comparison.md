# Model x prompt comparison

One run per cell. Each table covers only the programs that every model in it ran, so its means are like for like. A run that produced no program counts as an end-to-end failure; its component scores are left out. Costs are list-price estimates (DeepSeek at peak rates; it actually charged about a third of that off-peak).

Programs run per model: haiku-4-5 24, sonnet-5 7, deepseek-flash 16, gemini-3.1-flash-lite 20, llama-4-maverick 24, gpt-5.6-luna 24, qwen3.8-flash 24.

## 7 programs: haiku-4-5, sonnet-5, deepseek-flash, gemini-3.1-flash-lite, llama-4-maverick, gpt-5.6-luna, qwen3.8-flash

Domains: event 2, fitness 2, kitchen 2, lab 1.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | sonnet-5 baseline | sonnet-5 four-turn | deepseek-flash baseline | deepseek-flash four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn | llama-4-maverick baseline | llama-4-maverick four-turn | gpt-5.6-luna baseline | gpt-5.6-luna four-turn | qwen3.8-flash baseline | qwen3.8-flash four-turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Steps F1 | 0.56 | 0.91 | 0.58 | 0.90 | 0.36 | 0.93 | 0.48 | 0.75 | 0.52 | 0.88 | 0.52 | 0.92 | 0.37 | 0.92 |
| Durations accuracy | 0.99 | 0.92 | 0.99 | 0.94 | 1.00 | 0.93 | 0.90 | 0.95 | 0.99 | 0.97 | 0.80 | 0.87 | 0.84 | 0.95 |
| Relationships F1 | 0.30 | 0.64 | 0.27 | 0.55 | 0.13 | 0.54 | 0.26 | 0.47 | 0.29 | 0.58 | 0.21 | 0.61 | 0.19 | 0.64 |
| Resources recall | 0.60 | 0.72 | 0.60 | 0.62 | 0.63 | 0.72 | 0.46 | 0.59 | 0.72 | 0.50 | 0.56 | 0.73 | 0.73 | 0.58 |
| Track structure (Rand) | 0.89 | 0.91 | 0.81 | 0.81 | 1.00 | 0.87 | 0.84 | 0.79 | 0.93 | 0.96 | 0.75 | 0.82 | 0.82 | 0.73 |
| Unsupported steps | 60% | 2% | 52% | 4% | 75% | 5% | 50% | 5% | 55% | 0% | 60% | 3% | 72% | 5% |
| End-to-end pass | 29% | 43% | 43% | 57% | 14% | 43% | 0% | 14% | 14% | 43% | 29% | 43% | 29% | 43% |
| Produced a program | 100% | 100% | 100% | 86% | 71% | 71% | 100% | 100% | 100% | 71% | 100% | 100% | 100% | 100% |
| Cost per program (USD) | $0.046 | $0.091 | $0.255 | $0.508 | $0.047 | $0.081 | $0.006 | $0.018 | $0.006 | $0.012 | $0.007 | $0.018 | $0.023 | $0.040 |
| Output tokens per program | 6,492 | 10,683 | 22,573 | 39,553 | 36,565 | 55,536 | 2,214 | 6,132 | 5,563 | 8,220 | 5,259 | 10,632 | 46,228 | 76,400 |
| Validator fix rounds | 0.86 | 0.43 | 1.00 | 0.86 | 1.57 | 1.71 | 0.71 | 0.71 | 0.71 | 0.86 | 0.14 | 0.14 | 0.14 | 0.14 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | sonnet-5 | deepseek-flash | gemini-3.1-flash-lite | llama-4-maverick | gpt-5.6-luna | qwen3.8-flash |
|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass | pass | pass | pass | pass |
| event-product-launch-run-of-show | fail | pass | fail | fail | pass | pass | pass |
| fitness-hiit-circuit-intervals | pass | fail | pass | fail | pass | pass | pass |
| fitness-partner-upper-body-supersets | fail | pass | pass | fail | no program | fail | fail |
| kitchen-backyard-barbecue-smoker-grill | pass | pass | fail | fail | fail | fail | fail |
| kitchen-country-loaf-bread-bake | fail | no program | no program | fail | no program | fail | fail |
| lab-cell-passaging-hood-incubator | fail | fail | no program | fail | fail | fail | fail |

## 16 programs: haiku-4-5, deepseek-flash, gemini-3.1-flash-lite, llama-4-maverick, gpt-5.6-luna, qwen3.8-flash

Domains: event 4, fitness 4, kitchen 4, lab 4.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | deepseek-flash baseline | deepseek-flash four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn | llama-4-maverick baseline | llama-4-maverick four-turn | gpt-5.6-luna baseline | gpt-5.6-luna four-turn | qwen3.8-flash baseline | qwen3.8-flash four-turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Steps F1 | 0.50 | 0.92 | 0.39 | 0.88 | 0.52 | 0.75 | 0.57 | 0.85 | 0.52 | 0.92 | 0.32 | 0.91 |
| Durations accuracy | 0.86 | 0.93 | 0.90 | 0.96 | 0.94 | 0.90 | 0.96 | 0.96 | 0.82 | 0.93 | 0.87 | 0.96 |
| Relationships F1 | 0.25 | 0.63 | 0.14 | 0.57 | 0.27 | 0.48 | 0.30 | 0.57 | 0.23 | 0.66 | 0.12 | 0.57 |
| Resources recall | 0.55 | 0.53 | 0.60 | 0.66 | 0.47 | 0.53 | 0.59 | 0.43 | 0.54 | 0.64 | 0.56 | 0.50 |
| Track structure (Rand) | 0.80 | 0.92 | 0.87 | 0.89 | 0.83 | 0.78 | 0.90 | 0.90 | 0.71 | 0.86 | 0.75 | 0.77 |
| Unsupported steps | 61% | 1% | 72% | 5% | 47% | 8% | 50% | 1% | 56% | 2% | 77% | 4% |
| End-to-end pass | 12% | 56% | 19% | 44% | 12% | 31% | 6% | 38% | 19% | 56% | 12% | 62% |
| Produced a program | 100% | 100% | 62% | 62% | 100% | 94% | 94% | 81% | 100% | 100% | 100% | 100% |
| Cost per program (USD) | $0.044 | $0.088 | $0.047 | $0.079 | $0.006 | $0.019 | $0.006 | $0.012 | $0.007 | $0.018 | $0.021 | $0.040 |
| Output tokens per program | 6,003 | 10,063 | 36,560 | 53,268 | 2,407 | 6,636 | 5,209 | 7,907 | 5,066 | 9,948 | 43,928 | 75,227 |
| Validator fix rounds | 1.00 | 0.44 | 1.56 | 1.56 | 0.81 | 0.88 | 0.94 | 0.69 | 0.19 | 0.12 | 0.06 | 0.06 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | deepseek-flash | gemini-3.1-flash-lite | llama-4-maverick | gpt-5.6-luna | qwen3.8-flash |
|---|---|---|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass | pass | pass | pass |
| event-product-launch-run-of-show | fail | fail | fail | pass | pass | pass |
| event-theater-load-in-soundcheck | fail | pass | no program | fail | pass | pass |
| event-wedding-reception-timeline | pass | fail | pass | pass | fail | fail |
| fitness-hiit-circuit-intervals | pass | pass | fail | pass | pass | pass |
| fitness-partner-upper-body-supersets | fail | pass | fail | no program | fail | fail |
| fitness-rowing-erg-interval-session | pass | pass | fail | pass | pass | pass |
| fitness-swim-practice-lane-assignments | pass | pass | pass | fail | pass | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | fail | fail | fail | fail | fail |
| kitchen-country-loaf-bread-bake | fail | no program | fail | no program | fail | fail |
| kitchen-griddle-breakfast-for-six | pass | no program | pass | no program | fail | fail |
| kitchen-holiday-cookie-batch | fail | no program | fail | fail | pass | pass |
| lab-cell-passaging-hood-incubator | fail | no program | fail | fail | fail | fail |
| lab-elisa-plate-wash | fail | no program | fail | pass | pass | pass |
| lab-microbiology-streak-and-incubate | pass | no program | fail | fail | fail | pass |
| lab-pcr-and-gel | pass | pass | pass | fail | pass | pass |

## 20 programs: haiku-4-5, gemini-3.1-flash-lite, llama-4-maverick, gpt-5.6-luna, qwen3.8-flash

Domains: event 4, fitness 4, kitchen 6, lab 6.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | gemini-3.1-flash-lite baseline | gemini-3.1-flash-lite four-turn | llama-4-maverick baseline | llama-4-maverick four-turn | gpt-5.6-luna baseline | gpt-5.6-luna four-turn | qwen3.8-flash baseline | qwen3.8-flash four-turn |
|---|---|---|---|---|---|---|---|---|---|---|
| Steps F1 | 0.50 | 0.92 | 0.53 | 0.80 | 0.59 | 0.87 | 0.56 | 0.93 | 0.33 | 0.91 |
| Durations accuracy | 0.88 | 0.92 | 0.95 | 0.91 | 0.96 | 0.95 | 0.84 | 0.93 | 0.83 | 0.93 |
| Relationships F1 | 0.23 | 0.62 | 0.26 | 0.52 | 0.30 | 0.59 | 0.24 | 0.65 | 0.11 | 0.56 |
| Resources recall | 0.59 | 0.56 | 0.51 | 0.57 | 0.57 | 0.47 | 0.56 | 0.66 | 0.55 | 0.53 |
| Track structure (Rand) | 0.83 | 0.92 | 0.82 | 0.78 | 0.91 | 0.90 | 0.75 | 0.88 | 0.72 | 0.78 |
| Unsupported steps | 63% | 1% | 48% | 7% | 50% | 2% | 55% | 3% | 77% | 5% |
| End-to-end pass | 10% | 65% | 15% | 40% | 5% | 45% | 15% | 55% | 10% | 65% |
| Produced a program | 100% | 100% | 95% | 95% | 90% | 85% | 100% | 100% | 100% | 100% |
| Cost per program (USD) | $0.046 | $0.091 | $0.007 | $0.019 | $0.006 | $0.012 | $0.007 | $0.018 | $0.022 | $0.040 |
| Output tokens per program | 6,211 | 10,296 | 2,760 | 6,545 | 5,141 | 8,024 | 5,103 | 10,355 | 44,579 | 74,962 |
| Validator fix rounds | 1.05 | 0.55 | 1.00 | 0.80 | 1.05 | 0.70 | 0.20 | 0.25 | 0.10 | 0.05 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | gemini-3.1-flash-lite | llama-4-maverick | gpt-5.6-luna | qwen3.8-flash |
|---|---|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass | pass | pass |
| event-product-launch-run-of-show | fail | fail | pass | pass | pass |
| event-theater-load-in-soundcheck | fail | no program | fail | pass | pass |
| event-wedding-reception-timeline | pass | pass | pass | fail | fail |
| fitness-hiit-circuit-intervals | pass | fail | pass | pass | pass |
| fitness-partner-upper-body-supersets | fail | fail | no program | fail | fail |
| fitness-rowing-erg-interval-session | pass | fail | pass | pass | pass |
| fitness-swim-practice-lane-assignments | pass | pass | fail | pass | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | fail | fail | fail | fail |
| kitchen-country-loaf-bread-bake | fail | fail | no program | fail | fail |
| kitchen-griddle-breakfast-for-six | pass | pass | no program | fail | fail |
| kitchen-holiday-cookie-batch | fail | fail | fail | pass | pass |
| kitchen-sheet-pan-chicken-dinner | pass | pass | pass | pass | pass |
| kitchen-soup-and-salad-lunch | pass | pass | pass | fail | pass |
| lab-cell-passaging-hood-incubator | fail | fail | fail | fail | fail |
| lab-elisa-plate-wash | fail | fail | pass | pass | pass |
| lab-microbiology-streak-and-incubate | pass | fail | fail | fail | pass |
| lab-pcr-and-gel | pass | pass | fail | pass | pass |
| lab-plasmid-miniprep-digest | pass | pass | fail | pass | pass |
| lab-western-blot-transfer-block | pass | fail | pass | fail | fail |

## 24 programs: haiku-4-5, llama-4-maverick, gpt-5.6-luna, qwen3.8-flash

Domains: event 4, fitness 4, kitchen 10, lab 6.

| Metric | haiku-4-5 baseline | haiku-4-5 four-turn | llama-4-maverick baseline | llama-4-maverick four-turn | gpt-5.6-luna baseline | gpt-5.6-luna four-turn | qwen3.8-flash baseline | qwen3.8-flash four-turn |
|---|---|---|---|---|---|---|---|---|
| Steps F1 | 0.50 | 0.92 | 0.61 | 0.88 | 0.56 | 0.93 | 0.37 | 0.92 |
| Durations accuracy | 0.89 | 0.92 | 0.96 | 0.95 | 0.86 | 0.91 | 0.85 | 0.93 |
| Relationships F1 | 0.23 | 0.63 | 0.31 | 0.59 | 0.25 | 0.66 | 0.13 | 0.58 |
| Resources recall | 0.57 | 0.56 | 0.51 | 0.50 | 0.56 | 0.69 | 0.57 | 0.56 |
| Track structure (Rand) | 0.84 | 0.93 | 0.92 | 0.91 | 0.78 | 0.88 | 0.76 | 0.80 |
| Unsupported steps | 62% | 1% | 48% | 2% | 55% | 3% | 74% | 4% |
| End-to-end pass | 8% | 62% | 4% | 38% | 12% | 54% | 17% | 67% |
| Produced a program | 96% | 100% | 92% | 83% | 100% | 100% | 100% | 100% |
| Cost per program (USD) | $0.046 | $0.092 | $0.005 | $0.012 | $0.007 | $0.018 | $0.022 | $0.038 |
| Output tokens per program | 6,155 | 10,260 | 4,905 | 8,092 | 5,160 | 10,047 | 45,695 | 72,170 |
| Validator fix rounds | 1.04 | 0.62 | 0.96 | 0.83 | 0.21 | 0.21 | 0.12 | 0.04 |

End-to-end by program, four-turn prompt:

| Program | haiku-4-5 | llama-4-maverick | gpt-5.6-luna | qwen3.8-flash |
|---|---|---|---|---|
| event-conference-session-av-checks | pass | pass | pass | pass |
| event-product-launch-run-of-show | fail | pass | pass | pass |
| event-theater-load-in-soundcheck | fail | fail | pass | pass |
| event-wedding-reception-timeline | pass | pass | fail | fail |
| fitness-hiit-circuit-intervals | pass | pass | pass | pass |
| fitness-partner-upper-body-supersets | fail | no program | fail | fail |
| fitness-rowing-erg-interval-session | pass | pass | pass | pass |
| fitness-swim-practice-lane-assignments | pass | fail | pass | pass |
| kitchen-backyard-barbecue-smoker-grill | pass | fail | fail | fail |
| kitchen-country-loaf-bread-bake | fail | no program | fail | fail |
| kitchen-griddle-breakfast-for-six | pass | no program | fail | fail |
| kitchen-holiday-cookie-batch | fail | fail | pass | pass |
| kitchen-sheet-pan-chicken-dinner | pass | pass | pass | pass |
| kitchen-soup-and-salad-lunch | pass | pass | fail | pass |
| kitchen-thanksgiving-one-oven | fail | fail | fail | fail |
| kitchen-two-burner-three-course-dinner | fail | fail | pass | pass |
| kitchen-weekend-brunch | pass | no program | fail | pass |
| kitchen-weeknight-stir-fry | pass | fail | pass | pass |
| lab-cell-passaging-hood-incubator | fail | fail | fail | fail |
| lab-elisa-plate-wash | fail | pass | pass | pass |
| lab-microbiology-streak-and-incubate | pass | fail | fail | pass |
| lab-pcr-and-gel | pass | fail | pass | pass |
| lab-plasmid-miniprep-digest | pass | fail | pass | pass |
| lab-western-blot-transfer-block | pass | pass | fail | fail |

