"""Tests for LoadDataset node."""

import pytest
from tests.client import get_client


def test_load_dataset_node_info():
    """Node info should contain expected input/output fields."""
    client = get_client()
    nodes = client.studio.get_node_info(names="LoadDataset")
    assert "LoadDataset" in nodes
    info = nodes["LoadDataset"]
    assert "input" in info
    assert "output" in info
    assert info["input"]["required"]["dataset_path"][0] == "PATH"
    assert info["output"] == ["STRING"]
    assert info["output_name"] == ["dataset_path"]


def test_load_dataset_default_path():
    """Default path should be used when no dataset_path is provided."""
    client = get_client()
    nodes = client.studio.get_node_info(names="LoadDataset")
    info = nodes["LoadDataset"]
    assert info["input"]["required"]["dataset_path"][1]["default"] == "/workspace/datasets/openai/gsm8k"


if __name__ == "__main__":
    pytest.main()
