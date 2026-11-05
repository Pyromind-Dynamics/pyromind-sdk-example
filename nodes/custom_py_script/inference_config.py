"""Bundle model service settings for downstream workflow nodes."""

import json


def inference_config(endpoint: str, model_name: str, api_key: str = "") -> dict:
    return {
        "inference_config": json.dumps({
            "endpoint": endpoint,
            "model_name": model_name,
            "api_key": api_key,
        }),
    }
