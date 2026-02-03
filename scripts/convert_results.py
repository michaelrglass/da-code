#!/usr/bin/env python3
"""
Convert results from gpt-*.json format to result.json (Harbor) format.

Usage:
    python convert_results.py results/gpt-4o-787dbe9b.json -o results/converted.json
    python convert_results.py results/gpt-*.json  # converts all, writes to same dir
"""

import argparse
import json
import uuid
from collections import defaultdict
from pathlib import Path


def convert_results(source_data: dict) -> dict:
    """Convert gpt-*.json format to result.json format."""
    results = source_data.get("results", [])
    num_results = source_data.get("num_results", len(results))

    # Group results by score
    reward_stats: dict[str, list[str]] = defaultdict(list)
    exception_stats: dict[str, list[str]] = defaultdict(list)

    total_score = 0.0
    n_errors = 0

    for result in results:
        task_id = "dacode-" + result.get("id", "unknown") + "__aBaCada"
        score = result.get("total_score", 0.0)
        finished = result.get("finished", False)

        # Check for errors (unfinished or has error info)
        info = result.get("info", [])
        has_error = not finished or (info and any("error" in str(i).lower() for i in info))

        if has_error and not finished:
            exception_stats["AgentDidNotFinish"].append(task_id)
            n_errors += 1
        else:
            # Convert score to string key (normalize float representation)
            score_key = str(float(score))
            reward_stats[score_key].append(task_id)
            total_score += score

    n_trials = num_results
    mean_score = total_score / n_trials if n_trials > 0 else 0.0

    # Build output structure
    output = {
        "id": str(uuid.uuid4()),
        "n_total_trials": n_trials,
        "stats": {
            "n_trials": n_trials,
            "n_errors": 0,
            "evals": {
                "da-agent": {
                    "n_trials": n_trials,
                    "n_errors": 0,
                    "metrics": [
                        {
                            "mean": mean_score
                        }
                    ],
                    "reward_stats": {
                        "reward": dict(reward_stats)
                    }
                }
            }
        }
    }

    # Add exception_stats only if there are errors
    if exception_stats:
        output["stats"]["evals"]["da-agent"]["exception_stats"] = dict(exception_stats)

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Convert gpt-*.json format to result.json format"
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        type=Path,
        help="Input JSON file(s) in gpt-*.json format"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (only valid with single input file)"
    )
    args = parser.parse_args()

    if args.output and len(args.input_files) > 1:
        parser.error("--output can only be used with a single input file")

    for input_path in args.input_files:
        if not input_path.exists():
            print(f"Error: {input_path} does not exist")
            continue

        with open(input_path, "r") as f:
            source_data = json.load(f)

        converted = convert_results(source_data)

        if args.output:
            output_path = args.output
        else:
            # Generate output filename: gpt-4o-xxx.json -> gpt-4o-xxx.harbor.json
            output_path = input_path.with_suffix(".harbor.json")

        with open(output_path, "w") as f:
            json.dump(converted, f, indent=4)

        print(f"Converted {input_path} -> {output_path}")
        print(f"  Trials: {converted['stats']['n_trials']}")
        print(f"  Errors: {converted['stats']['n_errors']}")
        print(f"  Mean score: {converted['stats']['evals']['da-agent']['metrics'][0]['mean']:.4f}")


if __name__ == "__main__":
    main()
