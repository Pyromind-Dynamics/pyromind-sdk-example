"""Shared PyroMind API client with default environment variables."""

import os
from typing import Optional

from pyromind_sdk import PyroMindAPIClient

os.environ.setdefault("PYROMIND_BASE_URL", "https://api-portal.pyromind.ai/api/v1")
os.environ.setdefault("PYROMIND_CLUSTER", "us-west-2")


def get_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    cluster: Optional[str] = None,
) -> PyroMindAPIClient:
    """Create a PyroMindAPIClient.

    Priority: explicit parameter > env var > default value.
    """
    return PyroMindAPIClient(api_key=api_key, base_url=base_url, cluster=cluster)
