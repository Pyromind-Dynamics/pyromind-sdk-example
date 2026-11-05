"""Bundle benchmark worker and task selection settings."""

import json


def rollout_config(works: int, num_tasks: int = 1, start_index: int = 0) -> dict:
    return {
        "rollout_config": json.dumps({
            "works": works,
            "num_tasks": num_tasks,
            "start_index": start_index,
        }),
    }
