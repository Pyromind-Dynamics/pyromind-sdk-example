# /workspace/nodes/py_script/customer_node.py
def customer_function(name: str = "World") -> dict:
    """返回一个问候消息。"""
    return {"message": f"Hello, {name}! This is a customer node."}