import ast
import operator
from typing import Any, Dict
from mcp_skills.server.tools.registry import default_registry

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: lambda x: x,
}

def _safe_eval(node: Any) -> Any:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in operators:
            raise TypeError(f"Unsupported binary operator: {op}")
        return operators[op](_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in operators:
            raise TypeError(f"Unsupported unary operator: {op}")
        return operators[op](_safe_eval(node.operand))
    else:
        raise TypeError(f"Unsupported expression node: {type(node)}")

@default_registry.tool(
    name="calculator",
    description="Evaluate a basic arithmetic expression (+, -, *, /, %, **)",
    parameters={
        "type": "object",
        "properties": {"expression": {"type": "string", "description": "The math expression to evaluate"}},
        "required": ["expression"],
    },
)
def calculator(expression: str) -> dict[str, Any]:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return {"expression": expression, "result": float(result)}
    except Exception as e:
        return {"expression": expression, "error": str(e)}

@default_registry.tool(
    name="echo",
    description="Echo back the input message.",
    parameters={
        "type": "object",
        "properties": {"message": {"type": "string", "description": "The message to echo"}},
        "required": ["message"],
    },
)
def echo(message: str) -> dict[str, Any]:
    return {"message": message}
