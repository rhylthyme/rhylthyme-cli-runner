# rhylthyme

Rhylthyme schedules work that a person carries out against a clock: several
dishes that must land together, a lab protocol with overlapping incubations
and one centrifuge, an event run-of-show, a workout. A schedule is a small
JSON program of parallel tracks, timed steps and shared-equipment limits;
the deliverable is a live timeline with timers that you follow on a phone.

```bash
pip install rhylthyme
rhylthyme publish https://raw.githubusercontent.com/rhylthyme/.github/main/profile/examples/taco-night.json --image taco-night.png --open
```

This package installs three others:

| Package | Gives you |
|---|---|
| [rhylthyme-cli-runner](https://pypi.org/project/rhylthyme-cli-runner/) | the `rhylthyme` command: `validate` (offline), `analyze --finish-at 19:00` (conflicts, critical path, when to start each step), `publish` (a live timeline URL), `run` (timers in the terminal), `runs` and `calibrate` (learn real durations) |
| [rhylthyme-importers](https://pypi.org/project/rhylthyme-importers/) | `rhylthyme import`: recipes from TheMealDB, Spoonacular and recipe sites; protocols from protocols.io, Opentrons and Benchling; CookLang files |
| [rhylthyme-timeline](https://pypi.org/project/rhylthyme-timeline/) | `rhylthyme render`: publication-quality SVG, PNG and PDF figures of a schedule (needs Node.js) |

No account or API key is needed for any of these.

To run steps on lab instruments, add an extra; a local workcell file maps
each tool a program uses to an instrument:

| Extra | Instruments |
|---|---|
| `rhylthyme[galago]` | [galago-tools](https://github.com/sciencecorp/galago-tools): shakers, incubators, plate readers, liquid handlers, robot arms. See [rhylthyme-galago](https://github.com/rhylthyme/rhylthyme-galago) |
| `rhylthyme[labmcp]` | [LabMCP](https://github.com/K-Dense-AI/lab-instrument-mcps): balances, stirrers, syringe pumps, sensors, spectrometers, Opentrons, and SiLA 2, SCPI and Modbus devices. See [rhylthyme-labmcp](https://github.com/rhylthyme/rhylthyme-labmcp) |

```bash
pip install "rhylthyme[labmcp]"
rhylthyme validate protocol.json --workcell lab.json
rhylthyme run protocol.json --workcell lab.json   # simulated unless --live
```

Docs: https://docs.rhylthyme.com. Source: https://github.com/rhylthyme.
Version 0.1.0 of this name was an early internal library; if you depended on
`import rhylthyme` from it, pin `rhylthyme==0.1.0`.
