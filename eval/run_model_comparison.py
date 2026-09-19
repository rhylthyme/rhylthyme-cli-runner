#!/usr/bin/env python3
"""Run the prompt benchmark for another model under a hard spending cap.

Runs `rhylthyme eval-prompts` one gold program at a time so spending can be
checked between programs. Every live program's cost (as the harness computes
it from the API's token usage) is appended to a ledger file; the ledger
persists, so re-running this script never double-spends and the cap holds
across invocations. A program is only started when

    spent so far + reserve for one more program <= cap

where the reserve is 1.5x the most expensive program seen so far for that
pattern (or a conservative first guess). Programs are taken round-robin
across domains and each program runs every prompt before the next program
starts, so a run the cap cuts short is still balanced and still paired.

Afterwards each (model, pattern) cell is re-scored from its cache, which
costs nothing, to produce one consolidated results.json per cell.

    python eval/run_model_comparison.py --model claude-sonnet-5 --cap 6.50
    python eval/run_model_comparison.py --model claude-sonnet-5 --cap 6.50 --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD = HERE.parent.parent / "rhylthyme-examples" / "gold"
FIRST_GUESS = {
    "four-turn": 0.40,
    "baseline": 0.20,
}  # USD per program, before any is measured


def gold_slugs() -> list[str]:
    slugs = sorted(p.name for p in GOLD.iterdir() if p.is_dir())
    by_domain = defaultdict(list)
    for s in slugs:
        by_domain[s.split("-")[0]].append(s)
    rounds = zip_longest(*[by_domain[d] for d in sorted(by_domain)])
    return [s for group in rounds for s in group if s]


def load_ledger(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"entries": []}


def spent(ledger: dict) -> float:
    return round(sum(e["cost_usd"] for e in ledger["entries"]), 6)


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "rhylthyme_cli_runner.cli", "eval-prompts", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", required=True)
    ap.add_argument(
        "--cap",
        type=float,
        required=True,
        help="Hard limit on total USD recorded in the ledger.",
    )
    ap.add_argument("--patterns", default="four-turn,baseline")
    ap.add_argument("--out", type=Path, default=HERE / "models")
    ap.add_argument(
        "--ledger", type=Path, default=HERE / "models" / "spend-ledger.json"
    )
    ap.add_argument(
        "--max-programs",
        type=int,
        default=0,
        help="Only the first N programs of the domain round-robin order.",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(HERE.parent / "src"))
    from rhylthyme_cli_runner.eval.llm import price_for

    if price_for(args.model) is None:
        sys.exit(
            f"No price known for {args.model}: every run would be recorded as $0 and the cap would never trip.\n"
            "Add it to PRICES_PER_MTOK in eval/llm.py, or set RHYLTHYME_EVAL_PRICE_IN and RHYLTHYME_EVAL_PRICE_OUT (USD per million tokens)."
        )
    args.out.mkdir(parents=True, exist_ok=True)
    ledger = load_ledger(args.ledger)
    slugs = gold_slugs()
    done = {(e["model"], e["pattern"], e["slug"]) for e in ledger["entries"]}
    print(
        f"ledger: ${spent(ledger):.2f} spent of ${args.cap:.2f} cap; {len(slugs)} gold programs"
    )

    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
    if args.max_programs:
        slugs = slugs[: args.max_programs]

    def reserve_for(pattern: str) -> float:
        seen = [
            e["cost_usd"]
            for e in ledger["entries"]
            if e["model"] == args.model and e["pattern"] == pattern
        ]
        return 1.5 * max(seen) if seen else FIRST_GUESS.get(pattern, 0.40)

    # Slug outer, pattern inner: every program gets all its prompts or none,
    # so a run the cap cuts short is still a paired comparison.
    for slug in slugs:
        todo = [p for p in patterns if (args.model, p, slug) not in done]
        if not todo:
            continue
        need = sum(reserve_for(p) for p in todo)
        if spent(ledger) + need > args.cap:
            print(
                f"STOP before {slug}: ${spent(ledger):.2f} spent + ${need:.2f} reserve > ${args.cap:.2f} cap"
            )
            break
        for pattern in todo:
            cell = args.out / args.model / pattern
            if args.dry_run:
                print(f"would run {pattern}/{slug}")
                continue
            started = time.time()
            proc = run_cli(
                [
                    "--gold",
                    str(GOLD),
                    "--model",
                    args.model,
                    "--patterns",
                    pattern,
                    "--only",
                    slug,
                    "--out",
                    str(cell / "per-program" / slug),
                    "--cache-dir",
                    str(cell / "cache"),
                    "--format",
                    "json",
                ]
            )
            results_file = cell / "per-program" / slug / "results.json"
            if not results_file.exists():
                print(f"FAILED {pattern}/{slug}: {proc.stderr.strip()[-400:]}")
                sys.exit(2)  # never loop on an error that might be costing money
            totals = json.loads(results_file.read_text())["meta"]["totals"]
            cost = float(totals.get("cost_usd") or 0.0)
            entry = {
                "model": args.model,
                "pattern": pattern,
                "slug": slug,
                "cost_usd": cost,
                "input_tokens": totals.get("input_tokens"),
                "output_tokens": totals.get("output_tokens"),
                "calls": totals.get("calls"),
                "seconds": round(time.time() - started, 1),
            }
            ledger["entries"].append(entry)
            args.ledger.write_text(json.dumps(ledger, indent=1) + "\n")
            print(
                f"{pattern:10} {slug:45} ${cost:.3f}  total ${spent(ledger):.2f}  ({entry['seconds']:.0f}s)",
                flush=True,
            )

    if args.dry_run:
        return
    # Consolidate each cell from its cache: no model calls, no cost.
    for pattern in [p.strip() for p in args.patterns.split(",") if p.strip()]:
        cell = args.out / args.model / pattern
        ran = [
            e["slug"]
            for e in ledger["entries"]
            if e["model"] == args.model and e["pattern"] == pattern
        ]
        if not ran:
            continue
        proc = run_cli(
            [
                "--gold",
                str(GOLD),
                "--model",
                args.model,
                "--patterns",
                pattern,
                "--only",
                ",".join(ran),
                "--from-cache",
                "--cache-dir",
                str(cell / "cache"),
                "--out",
                str(cell),
                "--format",
                "json",
            ]
        )
        ok = (cell / "results.json").exists()
        print(
            f"consolidated {args.model}/{pattern}: {len(ran)} programs {'ok' if ok else 'FAILED ' + proc.stderr.strip()[-300:]}"
        )
    print(f"final: ${spent(ledger):.2f} of ${args.cap:.2f}")


if __name__ == "__main__":
    main()
