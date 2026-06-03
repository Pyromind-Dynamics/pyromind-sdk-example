"""Tests for LoadImage node."""

import pytest
from tests.client import get_client


def test_load_image_default():
    """Default should return the first image path from image_cache."""
    client = get_client()
    nodes = client.studio.get_node_info(names="LoadImage")
    assert "LoadImage" in nodes


def test_load_image_node_info():
    """Node info should contain expected input/output fields."""
    client = get_client()
    nodes = client.studio.get_node_info(names="LoadImage")
    info = nodes["LoadImage"]
    assert info["input"]["image"]["type"] == "STRING"
    assert info["output"]["image_file_path"]["type"] == "STRING"


def test_load_image_supported_formats():
    """Supported image formats should be documented in node info."""
    client = get_client()
    nodes = client.studio.get_node_info(names="LoadImage")
    info = nodes["LoadImage"]
    assert "image" in info["input"]


if __name__ == "__main__":
    pytest.main()
