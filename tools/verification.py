# =========================================================
# VERIFICATION TOOL
# =========================================================

import re


# =========================================================
# EXTRACT ARITHMETIC EXPRESSION
# =========================================================

def extract_numbers(expression):
    """
    Extract numeric values from a simple arithmetic
    expression.
    """

    numbers = re.findall(
        r"-?\d+(?:\.\d+)?",
        expression
    )

    return [
        float(number)
        for number in numbers
    ]


# =========================================================
# INDEPENDENT CALCULATION
# =========================================================

def independently_verify(expression):
    """
    Independently verify simple multiplication,
    addition, subtraction, and division operations.

    This function intentionally does not call the
    main calculator tool.
    """

    text = expression.lower().strip()

    numbers = extract_numbers(text)

    if len(numbers) < 2:
        return None

    first = numbers[0]
    second = numbers[1]


    # -----------------------------------------------------
    # MULTIPLICATION
    # -----------------------------------------------------

    if (
        "*" in text
        or "multiply" in text
        or "multiplication" in text
    ):

        return first * second


    # -----------------------------------------------------
    # ADDITION
    # -----------------------------------------------------

    if (
        "+" in text
        or "add" in text
        or "addition" in text
    ):

        return first + second


    # -----------------------------------------------------
    # SUBTRACTION
    # -----------------------------------------------------

    if (
        "-" in text
        or "subtract" in text
        or "subtraction" in text
    ):

        return first - second


    # -----------------------------------------------------
    # DIVISION
    # -----------------------------------------------------

    if (
        "/" in text
        or "divide" in text
        or "division" in text
    ):

        if second == 0:
            return None

        return first / second


    return None


# =========================================================
# VERIFY RESULT
# =========================================================

def verify_result(
    expression,
    tool_result
):
    """
    Compare a tool result with an independent
    calculation.

    Returns:

        {
            "verified": True/False,
            "original_result": ...,
            "verified_result": ...,
            "message": ...
        }
    """

    verified_result = (
        independently_verify(
            expression
        )
    )

    if verified_result is None:

        return {
            "verified": False,
            "original_result": tool_result,
            "verified_result": None,
            "message": (
                "Could not independently "
                "verify this operation."
            )
        }


    # -----------------------------------------------------
    # Numeric comparison
    # -----------------------------------------------------

    try:

        original_numeric = float(
            tool_result
        )

        verified_numeric = float(
            verified_result
        )

        is_correct = (
            abs(
                original_numeric
                - verified_numeric
            )
            < 1e-9
        )

    except (
        TypeError,
        ValueError
    ):

        is_correct = (
            str(tool_result).strip()
            ==
            str(verified_result).strip()
        )


    # -----------------------------------------------------
    # Correct
    # -----------------------------------------------------

    if is_correct:

        return {
            "verified": True,
            "original_result": tool_result,
            "verified_result": verified_result,
            "message": (
                "Tool result independently verified."
            )
        }


    # -----------------------------------------------------
    # Incorrect
    # -----------------------------------------------------

    return {
        "verified": False,
        "original_result": tool_result,
        "verified_result": verified_result,
        "message": (
            "Tool result was incorrect. "
            "Independent verification produced "
            f"{verified_result}."
        )
    }