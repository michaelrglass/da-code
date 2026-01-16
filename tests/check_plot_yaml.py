#!/usr/bin/env python3
"""
Script to check if plot.yaml files exist for tasks that reference them in their instructions.
"""

import json
import os
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    jsonl_file = base_dir / "da_code" / "configs" / "task" / "all.jsonl"
    source_dir = base_dir / "da_code" / "source"

    missing = []
    found = []

    with open(jsonl_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                task = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue

            task_id = task.get("id", "")
            instruction = task.get("instruction", "")

            # Check if instruction references plot.yaml
            if "plot.yaml" in instruction:
                plot_yaml_path = source_dir / task_id / "plot.yaml"

                if plot_yaml_path.exists():
                    found.append(task_id)
                else:
                    missing.append(task_id)

    print("=" * 60)
    print("Tasks referencing plot.yaml")
    print("=" * 60)
    print(f"\nTotal tasks referencing plot.yaml: {len(found) + len(missing)}")
    print(f"  - Found: {len(found)}")
    print(f"  - Missing: {len(missing)}")

    if missing:
        print(f"\n{'=' * 60}")
        print("MISSING plot.yaml files:")
        print("=" * 60)
        for task_id in sorted(missing):
            expected_path = source_dir / task_id / "plot.yaml"
            print(f"  - {task_id}: {expected_path}")

    return len(missing) == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
