#!/usr/bin/env python3
"""
Self-evaluation script to check that gold files score perfectly when compared to themselves.
This helps verify that the evaluation metrics are working correctly.
"""

import os
import sys
import json
import jsonlines
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

REPO_ROOT = Path(__file__).absolute().parent.parent
sys.path.append(str(REPO_ROOT / "da_agent" / "evaluators"))
import metrics


class SelfEvaluator:
    """Evaluates gold files against themselves to verify metrics return 1.0"""

    def __init__(self, gold_dir: str, eval_config_file: str):
        self.gold_dir = gold_dir
        self.eval_config_file = eval_config_file

    def get_result_file(self, results: List, dir: str):
        results = results if isinstance(results, list)\
            else [results]
        if 'number' in results[0].keys():
            return 'number', [results[0]['number']] 
        result_files = []
        for result in results:
            multi = result.get("multi", False)
            files = result['file'] if isinstance(result['file'], list) \
                else [result['file']]
            if multi:
                files = [os.path.join(dir, os.path.basename(file)) for file in files]
                result_files.append(files)
            else:
                for file in files:
                    file = os.path.basename(file)
                    # if not os.path.exists(os.path.join(dir, file)):
                    #     print(f"File not found : {os.path.join(dir, file)}")
                    result_files.append(os.path.join(dir, file))
        return 'file', result_files

    def evaluate_task(self, eval_config: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single task by comparing gold to itself"""
        task_id = eval_config['id']
        config = eval_config.get('config', {})
        task_type = config.get('task', 'unknown')
        result_type = config.get('type', 'unknown')
        hardness = config.get('hardness', 'unknown')

        # Get metric functions
        metric_funcs = eval_config["func"]
        metric_funcs = metric_funcs if isinstance(metric_funcs, list) else [metric_funcs]

        # Get metric options
        metric_options = eval_config.get("options", [{}])
        if not isinstance(metric_options, list):
            metric_options = [metric_options]
        metric_options = [opt if opt else {} for opt in metric_options]

        # Get gold files
        gold_id_dir = os.path.join(self.gold_dir, task_id)
        file_type, gold_files = self.get_result_file(eval_config['result'], gold_id_dir)

        # Check if gold files exist
        if file_type == 'file':
            missing_files = []
            for f in gold_files:
                if isinstance(f, list):
                    # Multi-file case
                    for sub_f in f:
                        if not os.path.exists(sub_f):
                            missing_files.append(sub_f)
                else:
                    if not os.path.exists(f):
                        missing_files.append(f)

            if missing_files:
                # print('*'*80)
                # print(f'WARNING: Missing files = {missing_files}')
                return {
                    "id": task_id,
                    "task": task_type,
                    "result_type": result_type,
                    "hardness": hardness,
                    "status": "missing_files",
                    "total_score": None,
                    "scores": [],
                    "details": [{"error": f"Missing: {missing_files}", "metric": "files"}]
                }

        # Expand metrics if needed
        if len(gold_files) > len(metric_funcs) and len(metric_funcs) == 1:
            metric_funcs = metric_funcs * len(gold_files)
            metric_options = metric_options * len(gold_files)

        # Evaluate each metric
        scores = []
        details = []

        for idx, func_name in enumerate(metric_funcs):
            gold_file = gold_files[idx]
            options = 'unset'
            try:
                metric_func = getattr(metrics, func_name)
                options = metric_options[idx].copy()

                # Add config to options if needed
                if config:
                    options['config'] = config

                # Compare gold to itself
                result = metric_func(gold_file, gold_file, **options)

                if isinstance(result, dict):
                    score = result.get('score', 0.0)
                    details.append({
                        "metric": func_name,
                        "options": options,
                        "score": score,
                        "gt": gold_file,
                        "details": result,
                    })
                else:
                    score = result
                    details.append({
                        "metric": func_name,
                        "options": options,
                        "score": score,
                        "gt": gold_file,
                    })

                scores.append(score)

            except Exception as e:
                
                scores.append(0.0)
                details.append({
                    "metric": func_name,
                    "options": options,
                    "score": 0.0,
                    "error": str(e),
                    "gt": gold_file,
                })

        # Calculate total score based on conjunction
        metric_conj = eval_config.get("conj", "avg")
        if metric_conj == 'avg':
            total_score = sum(scores) / len(scores) if scores else 0.0
        elif metric_conj == 'max':
            total_score = max(scores) if scores else 0.0
        elif metric_conj == 'min':
            total_score = min(scores) if scores else 0.0
        elif metric_conj == 'and':
            total_score = float(all(score != 0 for score in scores))
        elif metric_conj == 'or':
            total_score = float(any(score != 0 for score in scores))
        else:
            total_score = sum(scores) / len(scores) if scores else 0.0

        return {
            "id": task_id,
            "task": task_type,
            "result_type": result_type,
            "hardness": hardness,
            "status": "evaluated",
            "total_score": total_score,
            "scores": scores,
            "details": details
        }

    def evaluate_all(self) -> List[Dict[str, Any]]:
        """Evaluate all tasks in the config file"""
        # Load evaluation configs
        with jsonlines.open(self.eval_config_file, 'r') as js:
            eval_configs = [config for config in js]

        results = []
        failed_tasks = []
        perfect_score_count = 0

        print(f"\nEvaluating {len(eval_configs)} tasks...")
        print("=" * 80)

        pbar = tqdm(eval_configs, desc="Evaluating tasks")

        for eval_config in pbar:
            task_id = eval_config['id']
            pbar.set_description(f"Processing {task_id}")

            result = self.evaluate_task(eval_config)
            results.append(result)

            # Check if score is perfect
            if result['total_score'] == 1.0:
                perfect_score_count += 1
            else:
                failed_tasks.append(result)

        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tasks: {len(results)}")
        print(f"Perfect scores (1.0): {perfect_score_count}")
        print(f"Non-perfect scores: {len(failed_tasks)}")

        missing_files_count = sum(1 for r in results if r.get('status') == 'missing_files')
        if missing_files_count > 0:
            print(f"Missing gold files: {missing_files_count}")

        # Print failed tasks
        if failed_tasks:
            print("\n" + "=" * 80)
            print("TASKS WITH NON-PERFECT SCORES (POTENTIAL ISSUES)")
            print("=" * 80)
            for task in failed_tasks:
                print(f"\nTask: {task['id']}")
                print(f"  Type: {task['task']} / {task['result_type']}")
                print(f"  Hardness: {task['hardness']}")
                print(f"  Total Score: {task['total_score']}")
                print(f"  Individual Scores: {task['scores']}")
                if 'details' in task:
                    for detail in task['details']:
                        print(f"    Metric {detail['metric']}")
                        if 'options' in detail:
                            print(f"    Options {detail['options']}")
                        if 'error' in detail:
                            print(f"    Error: {detail['error']}")
                        if 'gt' in detail:
                            print(f"    Ground truth: {detail['gt']}")

        return results


def main():
    # Configuration
    gold_dir = str(REPO_ROOT / "da_code/gold")
    eval_config_file = str(REPO_ROOT / "da_code/configs/eval/eval_all.jsonl")

    # Check if files exist
    if not os.path.exists(eval_config_file):
        print(f"Error: Evaluation config file not found: {eval_config_file}")
        sys.exit(1)

    if not os.path.exists(gold_dir):
        print(f"Error: Gold directory not found: {gold_dir}")
        sys.exit(1)

    # Run evaluation
    evaluator = SelfEvaluator(gold_dir, eval_config_file)
    results = evaluator.evaluate_all()

    # Return exit code based on results
    failed_count = sum(1 for r in results if r.get('status') == 'evaluated' and r['total_score'] != 1.0)
    if failed_count > 0:
        print(f"\n⚠️  WARNING: {failed_count} task(s) did not achieve perfect score when comparing gold to itself!")
        sys.exit(1)
    else:
        print(f"\n✓ All evaluated tasks achieved perfect score (1.0)")
        sys.exit(0)


if __name__ == "__main__":
    main()
