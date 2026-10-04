import re

try:
    from agent.agent_state import AgentState
except ModuleNotFoundError:
    from agent_state import AgentState

from tools.calculator import calculate
from tools.time_tool import get_current_time
from tools.text_tool import count_words
from tools.verification import verify_result
from tools.weather_tool import format_weather_response, get_weather


# =========================================================
# HELPER: EXTRACT CALCULATOR EXPRESSION
# =========================================================

def normalize_calculation_expression(expression):
    if not expression:
        return expression

    normalized = expression.strip()
    normalized = normalized.replace("x", "*")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.replace("**", "**")
    return normalized


def is_calculation_step(step):
    if not step:
        return False

    step_lower = step.lower().strip()

    if any(
        keyword in step_lower
        for keyword in [
            "calculate",
            "compute",
            "multiply",
            "add",
            "subtract",
            "divide",
            "what is",
            "what's",
            "what is the value of",
        ]
    ):
        return True

    return bool(
        re.search(
            r"-?\d+(?:\.\d+)?\s*(?:\*\*|[\+\-\*\/x%])\s*-?\d+(?:\.\d+)?",
            step_lower,
        )
    )


def extract_calculator_expression(step):

    step_lower = step.lower().strip().rstrip("?!.")

    expression = None

    patterns = [
        r"(-?\d+(?:\.\d+)?)\s*(\*\*|[\+\-\*\/x%])\s*(-?\d+(?:\.\d+)?)",
        r"(-?\d+(?:\.\d+)?)\s+(?:x|×)\s+(-?\d+(?:\.\d+)?)",
        r"multiply\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)",
        r"add\s+(\d+(?:\.\d+)?)\s+(?:and|to)\s+(\d+(?:\.\d+)?)",
        r"subtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)",
        r"divide\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, step_lower)
        if not match:
            continue

        if len(match.groups()) == 3:
            left, operator, right = match.groups()
            operator = "**" if operator == "**" else operator.replace("x", "*").replace("×", "*")
            if operator in ["+", "-", "*", "/", "%"]:
                expression = f"{left} {operator} {right}"
            else:
                expression = f"{left} ** {right}"
        elif len(match.groups()) == 2:
            left, right = match.groups()
            expression = f"{left} * {right}"
        else:
            left, right = match.groups()
            expression = f"{left} * {right}"

        break

    if not expression:
        simple_match = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:\*|\/|\+|\-)\s*(-?\d+(?:\.\d+)?)", step_lower)
        if simple_match:
            expression = f"{simple_match.group(1)} {simple_match.group(0).split(simple_match.group(1))[1].strip()} {simple_match.group(2)}"

    if expression:
        expression = normalize_calculation_expression(expression)

    return expression


# =========================================================
# DETECT LEARNED VERIFICATION STRATEGY
# =========================================================

def extract_weather_location(step):
    text = (step or "").strip()
    patterns = [
        r"(?:weather|temperature|forecast)(?:\s+in|\s+for|\s+at|\s+of)?\s+([A-Za-z][A-Za-z\s'-]+?)(?:\?|\.|!|$)",
        r"(?:in|for|at|of)\s+([A-Za-z][A-Za-z\s'-]+?)(?:\?|\.|!|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if location and location.lower() not in {"the", "today", "tomorrow"}:
                return location
    return ""


def is_weather_step(step):
    if not step:
        return False
    step_lower = step.lower().strip()
    return "weather" in step_lower or "temperature" in step_lower or "forecast" in step_lower


def should_verify_result(learning_strategy):

    if not learning_strategy:
        return False

    strategy = learning_strategy.lower()

    verification_keywords = [
        "verify",
        "verification",
        "validate",
        "check the result",
        "check results",
        "independent verification"
    ]

    return any(
        keyword in strategy
        for keyword in verification_keywords
    )


# =========================================================
# TOOL EXECUTION
# =========================================================

def execute_tool_step(
    step,
    calculator_function=calculate,
    learning_strategy=""
):

    step_lower = step.lower().strip()

    # =====================================================
    # CALCULATOR
    # =====================================================

    if is_calculation_step(step):

        expression = extract_calculator_expression(step)

        # -------------------------------------------------
        # NO EXPRESSION
        # -------------------------------------------------

        if not expression:

            return {
                "success": False,
                "result": None,
                "error": "Could not extract calculator expression."
            }

        # -------------------------------------------------
        # EXECUTE CALCULATOR
        # -------------------------------------------------

        try:

            result = calculator_function(
                expression
            )

        except Exception as error:

            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

        # -------------------------------------------------
        # LEARNED VERIFICATION
        # -------------------------------------------------

        if should_verify_result(
            learning_strategy
        ):

            print(
                "🧠 Learned verification strategy detected."
            )

            print(
                "🔍 Independently verifying calculator result..."
            )

            verification = verify_result(
                expression,
                result
            )

            # ---------------------------------------------
            # VERIFICATION SUCCESS
            # ---------------------------------------------

            if verification["verified"]:

                print(
                    "✅ Verification passed."
                )

                return {
                    "success": True,
                    "result": verification[
                        "verified_result"
                    ],
                    "error": None,
                    "verified": True
                }

            # ---------------------------------------------
            # VERIFICATION FOUND ERROR
            # ---------------------------------------------

            if (
                verification["verified_result"]
                is not None
            ):

                print(
                    "⚠️ Calculator result was incorrect."
                )

                print(
                    "Original result:",
                    verification["original_result"]
                )

                print(
                    "Verified result:",
                    verification["verified_result"]
                )

                return {
                    "success": True,
                    "result": verification[
                        "verified_result"
                    ],
                    "error": None,
                    "verified": False,
                    "corrected": True
                }

            # ---------------------------------------------
            # VERIFICATION UNAVAILABLE
            # ---------------------------------------------

            print(
                "⚠️ Could not independently verify result."
            )

        # -------------------------------------------------
        # NORMAL CALCULATOR RESULT
        # -------------------------------------------------

        return {
            "success": True,
            "result": result,
            "error": None
        }

    # =====================================================
    # WEATHER
    # =====================================================

    if is_weather_step(step):
        location = extract_weather_location(step)
        try:
            weather_result = get_weather(location or step)
            if weather_result.get("success"):
                return {
                    "success": True,
                    "result": format_weather_response(weather_result),
                    "error": None,
                }
            return {
                "success": False,
                "result": None,
                "error": weather_result.get("error", "Weather information is unavailable."),
            }
        except Exception as error:
            return {
                "success": False,
                "result": None,
                "error": str(error),
            }

    # =====================================================
    # CURRENT TIME
    # =====================================================

    if (
        "current time" in step_lower
        or "what time" in step_lower
        or "current date" in step_lower
    ):

        try:

            result = get_current_time()

            return {
                "success": True,
                "result": result,
                "error": None
            }

        except Exception as error:

            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

    # =====================================================
    # WORD COUNTER
    # =====================================================

    if (
        "count the words" in step_lower
        or "count words" in step_lower
        or "word count" in step_lower
        or "number of words" in step_lower
    ):

        match = re.search(
            r"['\"](.*?)['\"]",
            step
        )

        if not match:

            return {
                "success": False,
                "result": None,
                "error": "Could not extract text for word counting."
            }

        text = match.group(1)

        try:

            result = count_words(text)

            return {
                "success": True,
                "result": result,
                "error": None
            }

        except Exception as error:

            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

    # =====================================================
    # UNKNOWN TOOL
    # =====================================================

    return {
        "success": False,
        "result": None,
        "error": "No suitable tool found for this step."
    }


# =========================================================
# EXECUTE PLAN
# =========================================================

def execute_plan(
    plan,
    state=None,
    learning_strategy="",
    calculator_function=calculate
):

    if isinstance(plan, str):
        parsed_steps = []
        for raw_line in plan.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = re.match(r"^\d+[\.)]?\s*(.+)$", line)
            if match:
                parsed_steps.append(match.group(1).strip())
            else:
                parsed_steps.append(line)
        plan = parsed_steps

    if state is None:
        state = AgentState("Plan execution", plan or [])

    state.start()

    print("\n" + "=" * 60)
    print("PLAN EXECUTION")
    print("=" * 60)

    while state.current_step < len(plan):

        step = plan[state.current_step]

        print(
            f"\nStep {state.current_step + 1}: {step}"
        )

        execution = execute_tool_step(
            step,
            calculator_function,
            learning_strategy
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if execution["success"]:

            result = execution["result"]

            print(
                "Result:",
                result
            )

            if execution.get("corrected"):

                print(
                    "🔧 Result corrected using independent verification."
                )

            state.complete_step(
                step,
                result
            )

            continue

        # -------------------------------------------------
        # FAILURE
        # -------------------------------------------------

        error = execution["error"]

        print(
            "Tool execution failed:",
            error
        )

        # -------------------------------------------------
        # LEARNED ERROR RECOVERY
        # -------------------------------------------------

        recovery_available = (
            learning_strategy
            and "retry" in learning_strategy.lower()
        )

        if recovery_available:

            print(
                "🧠 Learned recovery strategy detected."
            )

            if state.learned_retry():

                print(
                    "Applying learned strategy: RETRY"
                )

                continue

            print(
                "Learned retry limit reached."
            )

        # -------------------------------------------------
        # NORMAL RETRY
        # -------------------------------------------------

        if state.retry():

            print(
                "Applying normal retry mechanism."
            )

            continue

        # -------------------------------------------------
        # FINAL FAILURE
        # -------------------------------------------------

        state.fail(error)

        print(
            "Step permanently failed."
        )

        break

    # -----------------------------------------------------
    # FINISH
    # -----------------------------------------------------

    if (
        state.current_step >= len(plan)
        and len(plan) > 0
    ):

        state.finish()

        print(
            "\nPlan execution completed successfully."
        )

    return state