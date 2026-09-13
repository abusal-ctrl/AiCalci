from backend.tools.calculator_tool import calculate_tool


def calculate(expression: str) -> str:
    return calculate_tool(expression)