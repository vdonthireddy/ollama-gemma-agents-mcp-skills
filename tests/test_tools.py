from mcp_skills.server.tools.builtins import calculator, echo

def test_calculator_basic():
    res = calculator("6 * 7")
    assert res.get("result") == 42.0
    
    res = calculator("10 + 5 - 2")
    assert res.get("result") == 13.0
    
    res = calculator("2 ** 3")
    assert res.get("result") == 8.0

def test_calculator_safety():
    res = calculator("import os; os.system('ls')")
    assert "error" in res
    
    res = calculator("__import__('os')")
    assert "error" in res

def test_echo():
    res = echo("Hello World")
    assert res.get("message") == "Hello World"

def test_calculator_invalid_syntax():
    res = calculator("6 *")
    assert "error" in res

