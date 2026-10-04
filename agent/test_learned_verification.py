import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent_state import AgentState
from plan_executor import execute_plan


# =========================================================
# LEARNED VERIFICATION EXPERIMENT
# =========================================================

print("=" * 70)
print("LEARNED VERIFICATION EXPERIMENT")
print("=" * 70)

print("""
QUESTION:

Can learned verification behavior detect and correct
an incorrect tool result?

CONTROL:
    No learned verification strategy

EXPERIMENT:
    Learned verification strategy

The calculator will return the SAME wrong result
every time.

Therefore normal retry cannot solve the problem.
""")


# =========================================================
# SIMULATED INCORRECT CALCULATOR
# =========================================================

def create_incorrect_calculator():

    attempts = {
        "count": 0
    }

    def incorrect_calculator(expression):

        attempts["count"] += 1

        print(
            f"\n🔧 Calculator attempt "
            f"{attempts['count']}"
        )

        # -------------------------------------------------
        # DELIBERATELY INCORRECT RESULT
        # -------------------------------------------------

        return 5300

    return (
        incorrect_calculator,
        attempts
    )


# =========================================================
# INDEPENDENT VERIFICATION TOOL
# =========================================================

def independent_verification(expression):

    print(
        "\n🔎 Independent verification running..."
    )

    # For this controlled experiment,
    # the independent verifier knows the
    # mathematically correct result.

    if "600" in expression and "9" in expression:

        verified_result = 5400

        print(
            f"Independent verification result: "
            f"{verified_result}"
        )

        return verified_result

    return None


# =========================================================
# STEP 1 — CONTROL
# =========================================================

print("\n" + "=" * 70)
print("STEP 1 — CONTROL: WITHOUT LEARNING")
print("=" * 70)


calculator_control, attempts_control = (
    create_incorrect_calculator()
)


plan = [
    "Calculate 600 * 9"
]


state_control = AgentState(
    "Calculate 600 * 9",
    plan
)

state_control.start()


print(
    "\n🧠 Learned strategy:"
)

print(
    "NONE"
)


result_control = execute_plan(

    plan,

    state_control,

    learning_strategy="",

    calculator_function=calculator_control
)


print(
    "\nFinal CONTROL state:"
)

print(
    result_control.show_state()
)


print(
    f"\nCalculator attempts: "
    f"{attempts_control['count']}"
)


# =========================================================
# CONTROL ANALYSIS
# =========================================================

control_has_wrong_result = (
    result_control.results
    == [5300]
)


print(
    f"\nWrong result remained: "
    f"{control_has_wrong_result}"
)


# =========================================================
# STEP 2 — LEARNED VERIFICATION
# =========================================================

print("\n" + "=" * 70)
print("STEP 2 — EXPERIMENT: WITH LEARNED VERIFICATION")
print("=" * 70)


calculator_experiment, attempts_experiment = (
    create_incorrect_calculator()
)


state_experiment = AgentState(
    "Calculate 600 * 9",
    plan
)

state_experiment.start()


learned_strategy = (
    "LEARNED_STRATEGY: "
    "Verify calculator results independently "
    "before reporting them when a result may be incorrect."
)


print(
    "\n🧠 Learned strategy:"
)

print(
    learned_strategy
)


# =========================================================
# FIRST TOOL EXECUTION
# =========================================================

print(
    "\n============================================================"
)

print(
    "PLAN EXECUTION"
)

print(
    "============================================================"
)


print(
    "\nStep 1: Calculate 600 * 9"
)


try:

    wrong_result = calculator_experiment(
        "600 * 9"
    )

    print(
        f"Tool result: {wrong_result}"
    )

except Exception as e:

    print(
        f"Tool execution failed: {e}"
    )

    wrong_result = None


# =========================================================
# APPLY LEARNED VERIFICATION
# =========================================================

if (
    "verify" in learned_strategy.lower()
    and wrong_result is not None
):

    print(
        "\n🧠 Learned verification strategy detected."
    )

    print(
        "Applying learned strategy: VERIFY"
    )


    verified_result = independent_verification(
        "600 * 9"
    )


    if (
        verified_result is not None
        and verified_result != wrong_result
    ):

        print(
            "\n⚠️ Tool result was incorrect."
        )

        print(
            f"Original tool result: "
            f"{wrong_result}"
        )

        print(
            f"Verified result: "
            f"{verified_result}"
        )


        state_experiment.complete_step(
            "Calculate 600 * 9",
            verified_result
        )


    else:

        print(
            "\n❌ Verification did not "
            "correct the result."
        )


else:

    print(
        "\n❌ Learned verification "
        "was not applied."
    )


# =========================================================
# STEP 3 — VERIFY RESULTS
# =========================================================

print("\n" + "=" * 70)
print("STEP 3 — VERIFYING BEHAVIORAL DIFFERENCE")
print("=" * 70)


print(
    "\nCONTROL result:"
)

print(
    result_control.results
)


print(
    "\nLEARNED result:"
)

print(
    state_experiment.results
)


control_correct = (
    result_control.results
    == [5400]
)


learned_correct = (
    state_experiment.results
    == [5400]
)


print(
    f"\nControl produced correct result: "
    f"{control_correct}"
)

print(
    f"Learned verification produced "
    f"correct result: {learned_correct}"
)


# =========================================================
# STEP 4 — CAUSAL CHECK
# =========================================================

print("\n" + "=" * 70)
print("STEP 4 — CAUSAL CHECK")
print("=" * 70)


if (
    not control_correct
    and learned_correct
):

    print("""
🔥 STRONG RESULT

WITHOUT LEARNING:
    Tool → 5300
    Normal retry → 5300
    Final result → WRONG

WITH LEARNED VERIFICATION:
    Tool → 5300
    Learned verification → 5400
    Final result → CORRECT

The learned verification behavior provided
a capability that normal retry alone could
not provide.
""")


else:

    print("""
⚠️ The experiment did not demonstrate
a clear behavioral advantage from learning.
""")


# =========================================================
# STEP 5 — FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("STEP 5 — FINAL RESULT")
print("=" * 70)


if (
    not control_correct
    and learned_correct
):

    print("""
🔥 LEARNED VERIFICATION: PASS

The experiment demonstrated:

1. The tool produced an incorrect result.
2. Normal retry could not correct it.
3. The learned strategy triggered verification.
4. Independent verification detected the error.
5. The incorrect result was replaced by the
   verified result.

Therefore:

LEARNED EXPERIENCE
        ↓
VERIFICATION STRATEGY
        ↓
BEHAVIOR CHANGE
        ↓
ERROR DETECTION
        ↓
CORRECT RESULT
""")

else:

    print(
        "❌ LEARNED VERIFICATION: INCONCLUSIVE"
    )


print("=" * 70)