"""Bundle benchmark worker and task selection settings."""

import json


def rollout_config(
    inference_workers: int, grading_workers: int,
    num_tasks: int = 1, start_index: int = 0,
) -> dict:
    return {
        "rollout_config": json.dumps({
            "inference_workers": inference_workers,
            "grading_workers": grading_workers,
            "num_tasks": num_tasks,
            "start_index": start_index,
        }),
    }
