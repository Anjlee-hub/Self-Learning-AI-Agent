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
# INITIALIZE DATABASE
# =========================================================

init_db()


print("\n" + "=" * 70)
print("REAL SELF-LEARNING RECOVERY TEST")
print("ACTUAL EXECUTOR + CONTROLLED FAILURE")
print("=" * 70)


# =========================================================
# CONTROLLED CALCULATOR
# =========================================================

class ControlledCalculator:

    def __init__(self):

        self.attempts = 0


    def calculate(self, expression):

        self.attempts += 1

        print(
            f"\n[Controlled Calculator] Attempt #{self.attempts}"
        )


        # -------------------------------------------------
        # FIRST ATTEMPT ALWAYS FAILS
        # -------------------------------------------------

        if self.attempts == 1:

            print(
                "[Controlled Calculator] FAILURE"
            )

            raise RuntimeError(
                "Simulated first-attempt calculator failure"
            )


        # -------------------------------------------------
        # SECOND ATTEMPT SUCCEEDS
        # -------------------------------------------------

        print(
            "[Controlled Calculator] SUCCESS"
        )

        return 1000


# =========================================================
# STORE / RETRIEVE LEARNED RECOVERY STRATEGY
# =========================================================

print("\n" + "-" * 70)
print("LOADING LEARNED EXPERIENCE")
print("-" * 70)


failed_task = (
    "Calculate 250 * 4 using the Calculator tool"
)


failed_response = (
    "Calculator execution failed on the first attempt."
)


lesson_type = "ERROR_RECOVERY"


lesson = (
    "Retry the Calculator tool when the first execution "
    "fails before reporting the operation as unsuccessful."
)


# Store the experience

save_lesson(
    failed_task,
    failed_response,
    2,
    "NO",
    lesson_type,
    lesson
)


print(
    "Stored lesson:"
)

print(
    lesson
)


# Retrieve recovery lessons

recovery_lessons = get_lessons_by_type(
    "ERROR_RECOVERY",
    10
)


print(
    "\nERROR_RECOVERY lessons available:",
    len(recovery_lessons)
)


# ---------------------------------------------------------
# Select a retry strategy
# ---------------------------------------------------------

learning_strategy = ""


for item in recovery_lessons:

    stored_lesson = item[4]

    if "retry" in stored_lesson.lower():

        learning_strategy = (
            "LEARNED_STRATEGY: "
            + stored_lesson
        )

        break


print(
    "\nRetrieved learning:"
)

print(
    learning_strategy
)


# =========================================================
# CREATE REAL EXECUTOR STATE
# =========================================================

plan = [
    "Calculate 250 * 4"
]


state = AgentState(
    goal="Calculate 250 * 4",
    plan=plan
)


# ---------------------------------------------------------
# IMPORTANT
# ---------------------------------------------------------
#
# Disable the normal retry mechanism temporarily.
#
# We want this experiment to test whether the LEARNED
# strategy itself activates recovery.
#
# The learned strategy is allowed to retry.
#
# ---------------------------------------------------------

state.max_retries = 0


print("\n" + "-" * 70)
print("EXECUTING REAL PLAN EXECUTOR")
print("-" * 70)


# =========================================================
# RUN REAL EXECUTOR
# =========================================================

state = execute_plan(
    plan,
    state,
    learning_strategy=learning_strategy,
    calculator_function=ControlledCalculator().calculate
)


# =========================================================
# FINAL RESULTS
# =========================================================

print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)


print(
    "\nAgent state:"
)

print(
    state.show_state()
)


print(
    "\nFinal status:",
    state.status
)


if state.status == "completed":

    print(
        "\nLEARNED RECOVERY: SUCCESS"
    )

    print(
        "The real executor recovered from a tool failure "
        "using the learned strategy."
    )

else:

    print(
        "\nLEARNED RECOVERY: FAILED"
    )


print("\n" + "=" * 70)