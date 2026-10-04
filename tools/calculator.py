def calculate(expression):
    try:
        result = eval(expression)
        return result
    except Exception:
        return "Invalid calculation"