#!/usr/bin/env python3
"""Model x prompt comparison on the programs every cell has in common.

Reads the committed Haiku runs (eval/baseline.json, eval/four-turn.json) and
any cells under eval/models/<model>/<pattern>/results.json, restricts every
cell to the slugs ALL cells scored (so means are like for like), and writes
eval/models/comparison.md and comparison.csv. No model calls.

    python eval/compare_models.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "models"
METRICS = [
    ("steps_f1", "Steps F1", lambda p: p["steps"]["f1"]),
    ("durations_acc", "Durations accuracy", lambda p: p["durations"]["accuracy"]),
    ("relationships_f1", "Relationships F1", lambda p: p["relationships"]["f1"]),
    ("resources_recall", "Resources recall", lambda p: p["resources"]["recall"]),
    ("rand_index", "Track structure (Rand)", lambda p: p["structure"]["rand_index"]),
    ("unsupported", "Unsupported steps", lambda p: p["unsupported_rate"]),
    (
        "e2e",
        "End-to-end pass",
        lambda p: 1.0 if (p.get("end_to_end") or {}).get("passed") else 0.0,
    ),
    ("produced", "Produced a program", lambda p: 0.0 if p.get("error") else 1.0),
    ("cost_usd", "Cost per program (USD)", lambda p: p["extras"]["cost_usd"]),
    (
        "output_tokens",
        "Output tokens per program",
        lambda p: p["extras"]["output_tokens"],
    ),
    ("fix_iterations", "Validator fix rounds", lambda p: p["extras"]["fix_iterations"]),
]


ALWAYS = {
    m[2]
    for m in METRICS
    if m[0] in ("e2e", "produced", "cost_usd", "output_tokens", "fix_iterations")
}


def programs_of(path: Path) -> dict:
    data = json.loads(path.read_text())
    results = data.get("results", data)
    # Keep programs that errored (no program produced): they are failures,
    # and dropping them would flatter the model that produced them.
    return {p["slug"]: p for p in results["programs"]}


def value(fn, program):
    try:
        if program.get("error") and fn not in ALWAYS:
            return None  # component scores are undefined when nothing was produced
        v = fn(program)
        return float(v) if v is not None else None
    except (KeyError, TypeError):
        return None


def main() -> None:
    cells = {
        ("claude-haiku-4-5", "baseline"): programs_of(HERE / "baseline.json"),
        ("claude-haiku-4-5", "four-turn"): programs_of(HERE / "four-turn.json"),
    }
    for results in sorted(OUT.glob("*/*/results.json")):
        cells[(results.parent.parent.name, results.parent.name)] = programs_of(results)

    common = set.intersection(*(set(v) for v in cells.values()))
    slugs = sorted(common)
    domains = sorted({s.split("-")[0] for s in slugs})
    order = sorted(
        cells, key=lambda k: (k[0] != "claude-haiku-4-5", k[0], k[1] != "baseline")
    )

    def mean(cell, fn, subset=None):
        vals = [value(fn, cells[cell][s]) for s in (subset or slugs)]
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    def fmt(key, v):
        if v is None:
            return "n/a"
        if key == "cost_usd":
            return f"${v:.3f}"
        if key == "output_tokens":
            return f"{v:,.0f}"
        if key in ("e2e", "unsupported", "produced"):
            return f"{100 * v:.0f}%"
        return f"{v:.2f}"

    lines = [
        "# Model x prompt comparison",
        "",
        f"Programs scored in every cell: {len(slugs)} "
        f"({', '.join(f'{d} {sum(s.startswith(d) for s in slugs)}' for d in domains)}). "
        "One run per cell; means over those programs only. A run that produced no "
        "program counts as an end-to-end failure; its component scores are left out.",
        "",
        "| Metric | "
        + " | ".join(f"{m.replace('claude-', '')} {p}" for m, p in order)
        + " |",
        "|---|" + "---|" * len(order),
    ]
    rows = []
    for key, label, fn in METRICS:
        vals = [mean(c, fn) for c in order]
        lines.append(f"| {label} | " + " | ".join(fmt(key, v) for v in vals) + " |")
        rows.append([label] + [("" if v is None else round(v, 4)) for v in vals])

    lines += [
        "",
        "## End-to-end pass by program (four-turn)",
        "",
        "| Program | "
        + " | ".join(m.replace("claude-", "") for m, p in order if p == "four-turn")
        + " |",
        "|---|" + "---|" * sum(1 for _, p in order if p == "four-turn"),
    ]
    for s in slugs:
        marks = [
            (
                "no program"
                if cells[c][s].get("error")
                else (
                    "pass"
                    if (cells[c][s].get("end_to_end") or {}).get("passed")
                    else "fail"
                )
            )
            for c in order
            if c[1] == "four-turn"
        ]
        lines.append(f"| {s} | " + " | ".join(marks) + " |")

    OUT.mkdir(exist_ok=True)
    (OUT / "comparison.md").write_text("\n".join(lines) + "\n")
    with open(OUT / "comparison.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric"] + [f"{m}|{p}" for m, p in order])
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
