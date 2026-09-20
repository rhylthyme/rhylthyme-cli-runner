# Worked examples

Three complete programs, each valid as written (`rhylthyme validate --strict`),
with the reasoning that produced them and the arithmetic for working back from
a deadline. Copy one as a starting point, then change it.

## 1. Kitchen: everything lands together, around a step of unknown length

**Source.** "Roast chicken with mash and green beans for four. The chicken
takes about an hour and a quarter at 220 °C, until the thigh reads 74 °C, then
rests 15 minutes. Potatoes boil 20 to 30 minutes and get mashed. Beans take 8
minutes. One oven, a four-burner hob."

**Model.** Three tracks, one per dish, because each dish is a sequence that
cannot overlap itself. Resources: `oven: 1`, `burner: 4`, `counter: 2`.

**Steps, with the words they came from.** preheat 15 min (inferred: the source
gives a temperature and no preheat time); roast "about an hour and a quarter
... until the thigh reads 74 °C" is `indefinite` with `defaultSeconds` 75 min;
rest "rests 15 minutes" fixed; boil "20 to 30 minutes" `variable`; mash 5 min
(inferred); beans "8 minutes" fixed.

**Triggers.** The meal is ready when the rest ends, so the sides are anchored
to the roast, not to the clock. Potatoes need 25 + 5 = 30 min and must end with
the 15 min rest, so they start 15 min *before* the roast ends:
`afterStep roast, offsetSeconds: -900`. That negative offset is allowed only
because `roast` is `indefinite`. Beans need 8 min, so they start 15 − 8 = 7 min
*after* the roast ends. If the chicken takes 85 minutes instead of 75, the
person ends the roast late and the beans move with it.

```json
{
  "schemaVersion": "0.3.0-alpha",
  "programId": "roast-chicken-dinner",
  "name": "Roast chicken, mash and green beans",
  "environmentType": "kitchen",
  "tracks": [
    { "trackId": "oven", "name": "Oven", "steps": [
      {"stepId": "preheat", "name": "Preheat to 220 °C", "task": "oven", "duration": {"type": "fixed", "seconds": "15m"}, "startTrigger": {"type": "programStart"}},
      {"stepId": "roast", "name": "Roast chicken until 74 °C in the thigh", "task": "oven", "duration": {"type": "indefinite", "defaultSeconds": "75m"}, "startTrigger": {"type": "afterStep", "stepId": "preheat"}},
      {"stepId": "rest", "name": "Rest under foil, then carve", "task": "counter", "duration": {"type": "fixed", "seconds": "15m"}, "startTrigger": {"type": "afterStep", "stepId": "roast"}}
    ] },
    { "trackId": "potatoes", "name": "Potatoes", "steps": [
      {"stepId": "boil", "name": "Boil potatoes", "task": "burner", "duration": {"type": "variable", "minSeconds": "20m", "maxSeconds": "30m", "defaultSeconds": "25m"}, "startTrigger": {"type": "afterStep", "stepId": "roast", "offsetSeconds": -900}},
      {"stepId": "mash", "name": "Drain and mash", "task": "counter", "duration": {"type": "fixed", "seconds": "5m"}, "startTrigger": {"type": "afterStep", "stepId": "boil"}}
    ] },
    { "trackId": "beans", "name": "Green beans", "steps": [
      {"stepId": "blanch", "name": "Blanch and butter green beans", "task": "burner", "duration": {"type": "fixed", "seconds": "8m"}, "startTrigger": {"type": "afterStep", "stepId": "roast", "offsetSeconds": "7m"}}
    ] }
  ],
  "resourceConstraints": [
    {"task": "oven", "maxConcurrent": 1},
    {"task": "burner", "maxConcurrent": 4},
    {"task": "counter", "maxConcurrent": 2}
  ]
}
```

**Check.** Total length 1 h 45 min: preheat 15 + roast 75 + rest 15. Mash ends
at 75 + 25 + 5 = 105 min and beans at 97 + 8 = 105 min, so all three tracks end
together.

## 2. Event: a run of show with a flexible middle

**Source.** "Sound check at 5:00. Doors 5:30, welcome at 6:00 for ten minutes,
keynote about 45 minutes, then questions until the chair closes them, then an
hour's reception. Catering needs 25 minutes to set the reception and should be
done just before questions end. Record the keynote."

**Model.** Tracks are the things that can only do one thing at a time: the
stage, the AV desk, the catering crew. Each is also a resource with capacity 1.

**Triggers.** Times in the source are clock times; the program uses offsets
from its own start (5:00), so doors are `programStartOffset: 30m`. Recording
starts when the keynote *starts*: `afterStep keynote, event: "start"`. Catering
is anchored to the keynote's start plus 30 min, so it finishes 5 min before the
planned end of questions; anchoring it to the clock instead would leave it
wrong whenever the welcome overran.

```json
{
  "schemaVersion": "0.3.0-alpha",
  "programId": "evening-seminar",
  "name": "Evening seminar, run of show",
  "environmentType": "event",
  "tracks": [
    { "trackId": "stage", "name": "Stage", "steps": [
      {"stepId": "doors", "name": "Doors open, seating", "task": "stage", "duration": {"type": "fixed", "seconds": "30m"}, "startTrigger": {"type": "programStartOffset", "offsetSeconds": "30m"}},
      {"stepId": "welcome", "name": "Welcome and housekeeping", "task": "stage", "duration": {"type": "fixed", "seconds": "10m"}, "startTrigger": {"type": "afterStep", "stepId": "doors"}},
      {"stepId": "keynote", "name": "Keynote", "task": "stage", "duration": {"type": "variable", "minSeconds": "40m", "maxSeconds": "55m", "defaultSeconds": "45m"}, "startTrigger": {"type": "afterStep", "stepId": "welcome"}},
      {"stepId": "questions", "name": "Questions, until the chair closes", "task": "stage", "duration": {"type": "indefinite", "defaultSeconds": "15m"}, "startTrigger": {"type": "afterStep", "stepId": "keynote"}}
    ] },
    { "trackId": "av", "name": "Sound and slides", "steps": [
      {"stepId": "sound-check", "name": "Sound check with speaker", "task": "av-desk", "duration": {"type": "fixed", "seconds": "20m"}, "startTrigger": {"type": "programStart"}},
      {"stepId": "record", "name": "Record keynote", "task": "av-desk", "duration": {"type": "fixed", "seconds": "45m"}, "startTrigger": {"type": "afterStep", "stepId": "keynote", "event": "start"}}
    ] },
    { "trackId": "catering", "name": "Catering", "steps": [
      {"stepId": "set-reception", "name": "Set out drinks and canapés", "task": "catering-crew", "duration": {"type": "fixed", "seconds": "25m"}, "startTrigger": {"type": "afterStep", "stepId": "keynote", "event": "start", "offsetSeconds": "30m"}},
      {"stepId": "reception", "name": "Reception", "task": "catering-crew", "duration": {"type": "fixed", "seconds": "60m"}, "startTrigger": {"type": "afterStep", "stepId": "questions"}}
    ] }
  ],
  "resourceConstraints": [
    {"task": "stage", "maxConcurrent": 1},
    {"task": "av-desk", "maxConcurrent": 1},
    {"task": "catering-crew", "maxConcurrent": 1}
  ]
}
```

**Check.** Doors 0:30, welcome 1:00, keynote 1:10 to 1:55, questions to 2:10,
reception to 3:10. Total 3 h 10 min, so a 5:00 start ends at 8:10.

## 3. Laboratory: twelve samples through a rotor that holds six

**Source.** "Make master mix (10 min). Aliquot each of 12 samples into the
centrifuge (1 min each), spin 10 min, unload. The rotor holds six. When all
twelve are done, plate and run both thermocyclers (1 h), then analyse."

**Model.** One repeated chain, not twelve copied tracks. `replicates` on the
first step of the chain makes twelve instances; `instances: "each"` on the
steps after it makes each sample its own chain; `instances: "all"` is a
barrier that waits for every sample.

**The limit that matters.** `rotor: maxConcurrent 6` limits how many tubes are
in the rotor at one instant. `maxInFlight: 6` limits how many samples are
*between* entering the rotor and being unloaded, so sample 7 is not aliquoted
until sample 1 is out. Use `maxInFlight` whenever a slot stays occupied across
several steps (a rotor, a cooling rack, a water bath).

```json
{
  "schemaVersion": "0.3.0-alpha",
  "programId": "pcr-twelve-samples",
  "name": "Twelve samples, one rotor",
  "environmentType": "laboratory",
  "tracks": [
    { "trackId": "samples", "name": "Samples", "steps": [
      {"stepId": "master_mix", "name": "Prepare master mix", "task": "bench", "duration": {"type": "fixed", "seconds": 600}, "startTrigger": {"type": "programStart"}},
      {"stepId": "aliquot", "name": "Aliquot sample into rotor", "task": "rotor", "duration": {"type": "fixed", "seconds": 60}, "replicates": {"count": 12, "mode": "serial", "maxInFlight": 6}, "startTrigger": {"type": "afterStep", "stepId": "master_mix"}},
      {"stepId": "spin", "name": "Spin down sample", "task": "rotor", "duration": {"type": "fixed", "seconds": 600}, "startTrigger": {"type": "afterStep", "stepId": "aliquot", "instances": "each"}},
      {"stepId": "unload", "name": "Unload tube from rotor", "task": "bench", "duration": {"type": "fixed", "seconds": 60}, "startTrigger": {"type": "afterStep", "stepId": "spin", "instances": "each"}},
      {"stepId": "pcr", "name": "Thermocycler run", "task": "thermocycler", "duration": {"type": "fixed", "seconds": 3600}, "replicates": {"count": 2, "mode": "parallel"}, "startTrigger": {"type": "afterStep", "stepId": "unload", "instances": "all"}},
      {"stepId": "analysis", "name": "Analyse amplification curves", "task": "bench", "duration": {"type": "fixed", "seconds": 900}, "startTrigger": {"type": "afterStep", "stepId": "pcr", "instances": "all"}}
    ] }
  ],
  "resourceConstraints": [
    {"task": "bench", "maxConcurrent": 1, "description": "One technician at the bench"},
    {"task": "rotor", "maxConcurrent": 6, "description": "Centrifuge rotor holds six tubes"},
    {"task": "thermocycler", "maxConcurrent": 2, "description": "Two thermocyclers"}
  ]
}
```

**Check.** Total 1 h 54 min. The critical chain runs through the in-flight
limit: sample 7 waits for sample 1 to be unloaded at 22 min, sample 12 is
unloaded at 39 min, the thermocyclers run to 99 min and analysis ends at 114.

## Working back from a deadline

Programs hold durations and offsets, never clock times. To hit a deadline:

1. **Ask the tool.** `rhylthyme analyze program.json --finish-at 19:00` prints
   the start time and every step's local clock time. The rest of this list is
   the arithmetic behind it, for checking the answer.
2. **Start time = deadline − total length** (`defaultSeconds` stands in for
   variable and indefinite steps). Dinner at 19:00 with a 1 h 45 min
   program starts at 17:15. Imaging at 16:00 after a 5 h 20 min protocol starts
   at 10:40.
3. **Each step's clock time = start time + its offset in the plan.** In the
   kitchen example the potatoes go on at 17:15 + 75 min = 18:30.
4. **Add slack in front, not inside.** If the longest chain contains a
   `variable` or `indefinite` step, start earlier by the difference between its
   `maxSeconds` (or a realistic worst case) and its default. Do not pad step
   durations: padded steps make every timer wrong.
5. **Say the start time to the person** along with the URL. The timeline shows
   clock times once they press start.

To make several tracks end together, find the longest track (or the step
everything should land on), then delay each shorter track by the difference:
`programStartOffset` when the anchor is fixed, `afterStep` with an
`offsetSeconds` on the anchor when it is not. A negative `offsetSeconds`
("start 15 min before the roast ends") is accepted only when the anchor step
is `indefinite`; against a fixed step, count forward from the program start or
from an earlier step instead.

## Several protocols sharing one instrument

Put each protocol in its own track (or tracks), give the shared instrument one
`task` name used by both, and declare it once:

```json
{ "task": "thermocycler", "maxConcurrent": 1 }
```

Then run `rhylthyme analyze program.json --strict`. `validate` does not look
at timing, so it passes a program in which both protocols want the instrument
at once; `analyze` reports it, for example:

```
Resource conflicts (1):
- [maxConcurrent] `thermocycler` needs 2 but max is 1 from 0:00 to 1:00:00 (a-pcr, b-pcr)
```

Resolve it by delaying one protocol's first step with `programStartOffset`, or
by chaining its instrument step `afterStep` the other protocol's instrument
step, and analyze again until there are none. A cross-track `afterStep` is the
better fix when the first use has a variable or indefinite length.
