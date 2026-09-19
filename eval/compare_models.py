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


def short(model: str) -> str:
    """Column label: drop the vendor prefix."""
    return model.split("/")[-1].replace("claude-", "")


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
        # Directory names flatten "vendor/model" to "vendor__model".
        cells[(results.parent.parent.name.replace("__", "/"), results.parent.name)] = (
            programs_of(results)
        )

    order = sorted(
        cells, key=lambda k: (k[0] != "claude-haiku-4-5", k[0], k[1] != "baseline")
    )
    models = []
    for m, _ in order:
        if m not in models:
            models.append(m)
    coverage = {
        m: set.intersection(*(set(v) for (mm, _), v in cells.items() if mm == m))
        for m in models
    }

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

    def table(chosen, rows_out):
        """One like-for-like table over the programs every chosen model ran."""
        slugs = sorted(set.intersection(*(coverage[m] for m in chosen)))
        cols = [c for c in order if c[0] in chosen]
        domains = sorted({s.split("-")[0] for s in slugs})
        out = [
            f"## {len(slugs)} programs: " + ", ".join(short(m) for m in chosen),
            "",
            "Domains: "
            + ", ".join(f"{d} {sum(s.startswith(d) for s in slugs)}" for d in domains)
            + ".",
            "",
            "| Metric | " + " | ".join(f"{short(m)} {p}" for m, p in cols) + " |",
            "|---|" + "---|" * len(cols),
        ]
        for key, label, fn in METRICS:
            vals = []
            for c in cols:
                got = [value(fn, cells[c][s]) for s in slugs]
                got = [v for v in got if v is not None]
                vals.append(sum(got) / len(got) if got else None)
            out.append(f"| {label} | " + " | ".join(fmt(key, v) for v in vals) + " |")
            for (m, pat), v in zip(cols, vals):
                rows_out.append(
                    [len(slugs), label, m, pat, "" if v is None else round(v, 4)]
                )
        four = [c for c in cols if c[1] == "four-turn"]
        out += [
            "",
            "End-to-end by program, four-turn prompt:",
            "",
            "| Program | " + " | ".join(short(m) for m, _ in four) + " |",
            "|---|" + "---|" * len(four),
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
                for c in four
            ]
            out.append(f"| {s} | " + " | ".join(marks) + " |")
        return out + [""]

    # One table per coverage level: every model, then progressively only the
    # models that ran more programs, so a small run does not shrink the rest.
    lines = [
        "# Model x prompt comparison",
        "",
        "One run per cell. Each table covers only the programs that every model in it ran, so its "
        "means are like for like. A run that produced no program counts as an end-to-end failure; "
        "its component scores are left out. Costs are list-price estimates (DeepSeek at peak rates; "
        "it actually charged about a third of that off-peak).",
        "",
        "Programs run per model: "
        + ", ".join(f"{short(m)} {len(coverage[m])}" for m in models)
        + ".",
        "",
    ]
    rows: list = []
    seen_sets = []
    for size in sorted({len(v) for v in coverage.values()}):
        chosen = [m for m in models if len(coverage[m]) >= size]
        if len(chosen) < 2 or chosen in seen_sets:
            continue
        seen_sets.append(chosen)
        lines += table(chosen, rows)

    OUT.mkdir(exist_ok=True)
    (OUT / "comparison.md").write_text("\n".join(lines) + "\n")
    with open(OUT / "comparison.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_programs", "metric", "model", "prompt", "value"])
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
