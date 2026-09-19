# eval-prompts results

Generated: 2026-09-19T17:11:57+00:00
Gold: `/Volumes/My12tb/dev/rhylthyme-split/rhylthyme-examples/gold`
Predicted: ``

| program | steps P/R/F1 | dur acc | res P/R | actors | rel P/R/F1 | tracks RI | e2e | unsupp |
|---|---|---|---|---|---|---|---|---|
| event-conference-session-av-checks | 1.00/0.25/0.40 | 1.00 | 0.80/0.67 | 0.00 | 0.60/0.15/0.24 | 0.70 | 0.00 | 0.64 |
| **mean (n=1)** | **1.00/0.25/0.40** | **1.00** | **0.80/0.67** | **0.00** | **0.60/0.15/0.24** | **0.70** | **0.00** | **0.64** |

JS validator: ran on 1/1 programs

## End-to-end failures

- `event-conference-session-av-checks`: makespan 7920s vs gold 15240s; critical path overlap 0.06
