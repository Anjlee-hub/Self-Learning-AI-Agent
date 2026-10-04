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
# LEARNED BEHAVIOR EXECUTION TEST
# =========================================================

print("=" * 70)
print("LEARNED BEHAVIOR EXECUTION TEST")
print("=" * 70)

print("""
Goal:

LEARNED RECOVERY STRATEGY
          ↓
     PLAN EXECUTOR
          ↓
   TOOL FAILURE
          ↓
   AUTOMATIC RETRY
          ↓
        SUCCESS
""")


# =========================================================
# TEST TOOL
# =========================================================

attempts = {
    "count": 0
}


def simulated_calculator(expression):
    """
    Simulates a calculator that fails once
    and succeeds on the second attempt.
    """

    attempts["count"] += 1

    print(
        f"\n🔧 Simulated calculator attempt "
        f"{attempts['count']}"
    )

    # -----------------------------------------------------
    # First attempt deliberately fails
    # -----------------------------------------------------

    if attempts["count"] == 1:

        raise RuntimeError(
            "Simulated calculator failure"
        )

    # -----------------------------------------------------
    # Second attempt succeeds
    # -----------------------------------------------------

    return 600


# =========================================================
# STEP 1 — CREATE AGENT STATE
# =========================================================

print("\n" + "=" * 70)
print("STEP 1 — CREATE AGENT STATE")
print("=" * 70)


plan = [
    "Calculate 750 * 6"
]


state = AgentState(
    "Calculate 750 * 6",
    plan
)


state.start()


print("\nInitial state:")
print(
    state.show_state()
)


# =========================================================
# STEP 2 — PROVIDE LEARNED STRATEGY
# =========================================================

print("\n" + "=" * 70)
print("STEP 2 — APPLY LEARNED STRATEGY")
print("=" * 70)


learning_strategy = (
    "LEARNED_STRATEGY: "
    "Retry the calculator tool when the first "
    "execution fails before reporting the operation "
    "as unsuccessful."
)


print("\n🧠 Learned strategy:")
print(learning_strategy)


# =========================================================
# STEP 3 — EXECUTE PLAN
# =========================================================

print("\n" + "=" * 70)
print("STEP 3 — EXECUTE WITH LEARNED STRATEGY")
print("=" * 70)


final_state = execute_plan(
    plan,
    state,
    learning_strategy=learning_strategy,
    calculator_function=simulated_calculator
)


# =========================================================
# STEP 4 — VERIFY BEHAVIOR CHANGE
# =========================================================

print("\n" + "=" * 70)
print("STEP 4 — VERIFY BEHAVIORAL CHANGE")
print("=" * 70)


print("\nFinal state:")
print(
    final_state.show_state()
)


print(
    f"\nTotal tool attempts: "
    f"{attempts['count']}"
)


if attempts["count"] >= 2:

    print(
        "\n✅ The executor retried the failed operation."
    )

else:

    print(
        "\n❌ The executor did not retry."
    )

    print(
        "\nLEARNED BEHAVIOR TEST: FAIL"
    )

    sys.exit(1)


if final_state.status == "completed":

    print(
        "\n✅ The task eventually completed successfully."
    )

else:

    print(
        "\n❌ The task did not complete."
    )

    print(
        "\nLEARNED BEHAVIOR TEST: FAIL"
    )

    sys.exit(1)


# =========================================================
# STEP 5 — FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("STEP 5 — FINAL RESULT")
print("=" * 70)

print("""
The executor demonstrated:

1. First tool attempt failed.
2. Learned recovery strategy was available.
3. Executor retried the failed operation.
4. Second attempt succeeded.
5. Agent state reached COMPLETED.

Therefore:

LEARNED STRATEGY
       ↓
EXECUTOR BEHAVIOR
       ↓
AUTOMATIC RETRY
       ↓
SUCCESS

🔥 LEARNED BEHAVIOR EXECUTION: PASS
""")

print("=" * 70)