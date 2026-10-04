import sys
import os

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORTS
# =========================================================

from memory.memory import (
    init_db,
    save_lesson,
    get_lessons_by_type
)

from agent.plan_executor import execute_plan
from agent.agent_state import AgentState


# =========================================================
# INITIALIZE
# =========================================================

init_db()


print("\n" + "=" * 65)
print("REAL EXECUTOR LEARNING INTEGRATION TEST")
print("=" * 65)


# =========================================================
# TEST PLAN
# =========================================================

plan = [
    "Calculate 250 * 4"
]


# =========================================================
# LEARNED RECOVERY STRATEGY
# =========================================================

learning_strategy = (
    "LEARNED_STRATEGY: Retry the Calculator tool "
    "when the first execution fails."
)


# =========================================================
# EXECUTION
# =========================================================

print("\nLearned strategy:")
print(learning_strategy)


state = AgentState(
    goal="Calculate 250 * 4",
    plan=plan
)


# =========================================================
# EXECUTE
# =========================================================

state = execute_plan(
    plan,
    state,
    learning_strategy
)


# =========================================================
# RESULT
# =========================================================

print("\n" + "=" * 65)
print("EXECUTOR RESULT")
print("=" * 65)

print(
    "\nFinal state:"
)

print(
    state.show_state()
)


if state.status == "completed":

    print(
        "\nEXECUTOR RECOVERY: SUCCESS"
    )

else:

    print(
        "\nEXECUTOR RECOVERY: FAILED"
    )


print("\n" + "=" * 65)