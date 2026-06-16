# /workspace/nodes/custom_py_script/custom_node.py
def custom_function(name: str = "World") -> dict:
    """返回一个问候消息。"""
    return {"message": f"Hello, {name}! This is a custom node."}