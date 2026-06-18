# Load Anything From File Node

![alt text](/imgs/LoadAnythingFromFileNode/LoadAnythingFromFileNode.png)

## 1.1 Overview

Load content from a file path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| file_path | STRING | Yes | - |
| encoding | STRING | No | Default: `utf-8` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| loaded_file_path | STRING | loaded_file_path |
| content | * | content |
| read_bytes | INT | read_bytes |

## 1.4 Workflow JSON Definition

See [`workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json`](../../workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `loadAnythingFromFileNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json --pretty
```

Example output:

```json
{
  "task_id": "4874",
  "task_name": "unsaved-workflow",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18880,
      "node_type": "LoadAnythingFromFileNode",
      "label": "",
      "start_at": "2026-06-09 03:09:56",
      "end_at": "2026-06-09 03:10:10",
      "duration": "0:00:14",
      "input": {
        "file_path": "/workspace/py/example_valid_node.py",
        "encoding": "utf-8"
      },
      "output": {
        "loaded_file_path": "/workspace/py/example_valid_node.py",
        "content": "\"\"\"\n示例：符合验证规则的自定义节点\n- 基础类型: str, int, float, bool\n- 泛型类型: List[str], Optional[int]\n\"\"\"\n\nfrom typing import List, Optional\n\ndef process_data(a: int, b: int):\n    result = a + b\n    return {\"sum\": result, \"count\": 1, \"ok\": True}\n\n\ndef process_text(text: str, count: int) -> str:\n    \"\"\"处理文本并返回结果\"\"\"\n    return f\"Processed: {text} x {count}\"\n\n\ndef process_text_yaml(text1: str, text2: str, text3: str, count: int) -> str:\n    \"\"\"处理文本并返回结果\"\"\"\n    return f\"Processed: {text1} x {text2}x {text3} x {count}\"\n\ndef calculate_sum(numbers: List[int], scale: float) -> float:\n    \"\"\"计算列表总和并乘以缩放因子\"\"\"\n    total = sum(numbers)\n    return total * scale\n\n\ndef merge_strings(items: List[str], separator: str) -> str:\n    \"\"\"合并字符串列表\"\"\"\n    return separator.join(items)\n\n\ndef get_optional_value(name: str, default: Optional[str]) -> str:\n    \"\"\"获取可选值，如果为空则返回默认值\"\"\"\n    return name if name else (default or \"\")\n\n\ndef check_flag(enabled: bool, threshold: float) -> bool:\n    \"\"\"检查标志和阈值\"\"\"\n    return enabled and threshold > 0.5\n\n\nclass ExampleNode:\n    \"\"\"示例节点类\"\"\"\n    \n    def run(self, input_text: str, iterations: int) -> str:\n        \"\"\"执行节点逻辑\"\"\"\n        result = input_text * iterations\n        return result\n    \n    def process_batch(self, items: List[str]) -> List[str]:\n        \"\"\"批量处理\"\"\"\n        return [item.upper() for item in items]\n    \n    def calculate(self, values: List[float], multiplier: float) -> float:\n        \"\"\"计算加权值\"\"\"\n        return sum(values) * multiplier\n    \n    def check_status(self, is_active: bool, priority: int) -> bool:\n        \"\"\"检查状态\"\"\"\n        return is_active and priority > 0",
        "read_bytes": "1814"
      },
      "raw": {}
    }
  ]
}
```
