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
# KILLCRITIC CONTROL EXPERIMENT
# =========================================================

print("=" * 70)
print("KILLCRITIC LEARNING CONTROL EXPERIMENT")
print("=" * 70)

print("""
QUESTION:

Does the agent retry because of normal retry logic,
or because of the LEARNED recovery strategy?

CONTROL:
    No learned strategy

EXPERIMENT:
    Learned retry strategy

Both use the exact same failing tool.
""")


# =========================================================
# SHARED SIMULATED TOOL
# =========================================================

def create_failing_tool():

    attempts = {
        "count": 0
    }

    def simulated_calculator(expression):

        attempts["count"] += 1

        print(
            f"\n🔧 Calculator attempt "
            f"{attempts['count']}"
        )

        # First attempt always fails
        if attempts["count"] == 1:

            raise RuntimeError(
                "Simulated calculator failure"
            )

        # Second attempt succeeds
        return 5400

    return (
        simulated_calculator,
        attempts
    )


# =========================================================
# TEST 1 — WITHOUT LEARNING
# =========================================================

print("\n" + "=" * 70)
print("TEST 1 — WITHOUT LEARNED STRATEGY")
print("=" * 70)


tool_without_learning, attempts_without_learning = (
    create_failing_tool()
)


plan = [
    "Calculate 600 * 9"
]


state_without_learning = AgentState(
    "Calculate 600 * 9",
    plan
)


state_without_learning.start()


print(
    "\n🧠 Learned strategy:"
)

print(
    "NONE"
)


result_without_learning = execute_plan(

    plan,

    state_without_learning,

    learning_strategy="",

    calculator_function=tool_without_learning
)


print(
    "\nFinal state WITHOUT learning:"
)

print(
    result_without_learning.show_state()
)


print(
    f"\nTool attempts WITHOUT learning: "
    f"{attempts_without_learning['count']}"
)


# =========================================================
# TEST 2 — WITH LEARNING
# =========================================================

print("\n" + "=" * 70)
print("TEST 2 — WITH LEARNED STRATEGY")
print("=" * 70)


tool_with_learning, attempts_with_learning = (
    create_failing_tool()
)


state_with_learning = AgentState(
    "Calculate 600 * 9",
    plan
)


state_with_learning.start()


learned_strategy = (
    "LEARNED_STRATEGY: "
    "Retry the calculator tool when the first "
    "execution fails before reporting the operation "
    "as unsuccessful."
)


print(
    "\n🧠 Learned strategy:"
)

print(
    learned_strategy
)


result_with_learning = execute_plan(

    plan,

    state_with_learning,

    learning_strategy=learned_strategy,

    calculator_function=tool_with_learning
)


print(
    "\nFinal state WITH learning:"
)

print(
    result_with_learning.show_state()
)


print(
    f"\nTool attempts WITH learning: "
    f"{attempts_with_learning['count']}"
)


# =========================================================
# ANALYSIS
# =========================================================

print("\n" + "=" * 70)
print("KILLCRITIC ANALYSIS")
print("=" * 70)


without_learning_completed = (
    result_without_learning.status
    == "completed"
)


with_learning_completed = (
    result_with_learning.status
    == "completed"
)


without_learning_attempts = (
    attempts_without_learning["count"]
)


with_learning_attempts = (
    attempts_with_learning["count"]
)


print(
    f"\nWithout learning completed: "
    f"{without_learning_completed}"
)

print(
    f"With learning completed: "
    f"{with_learning_completed}"
)

print(
    f"Without learning attempts: "
    f"{without_learning_attempts}"
)

print(
    f"With learning attempts: "
    f"{with_learning_attempts}"
)


# =========================================================
# CRITICAL INTERPRETATION
# =========================================================

if (
    without_learning_completed
    and with_learning_completed
):

    print("""
⚠️ IMPORTANT:

Both versions completed successfully.

This means the current executor already has
NORMAL RETRY behavior.

Therefore, this experiment does NOT prove that
learning was necessary for recovery.

Learning successfully influenced the executor,
but normal retry logic can also recover.
""")


elif (
    not without_learning_completed
    and with_learning_completed
):

    print("""
🔥 STRONG RESULT:

WITHOUT LEARNING
    ↓
FAILURE

WITH LEARNING
    ↓
RETRY
    ↓
SUCCESS

This provides strong evidence that the learned
strategy caused the behavioral improvement.
""")


else:

    print("""
⚠️ INCONCLUSIVE RESULT.

The executor behavior needs further investigation.
""")


# =========================================================
# FINAL
# =========================================================

print("\n" + "=" * 70)
print("CONTROL EXPERIMENT COMPLETED")
print("=" * 70)