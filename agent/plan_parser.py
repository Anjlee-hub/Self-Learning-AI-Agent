import re


# =========================================================
# PLAN PARSER
# =========================================================

def parse_plan(plan_text):
    """
    Extract only numbered executable steps from an LLM plan.

    The planner may sometimes return explanations before or
    after the numbered list. Those lines must never become
    executable tool steps.
    """

    if not plan_text:
        return []

    steps = []

    # -----------------------------------------------------
    # Match numbered lines:
    #
    # 1. Calculate 25 * 4
    # 2. Get the current time
    #
    # Also supports:
    # 1) Calculate...
    # -----------------------------------------------------

    matches = re.findall(
        r"(?m)^\s*\d+[\.\)]\s*(.+?)\s*$",
        plan_text
    )

    for match in matches:

        step = match.strip()

        if not step:
            continue

        # -------------------------------------------------
        # Remove accidental trailing punctuation
        # -------------------------------------------------

        step = step.strip()

        steps.append(step)

    return steps