import sys
import os

# =========================================================
# ADD PROJECT ROOT TO PYTHON PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORT MEMORY
# =========================================================

from memory.memory import (
    init_db,
    save_lesson,
    get_lessons_by_type
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


print("\n" + "=" * 65)
print("BEHAVIORAL SELF-LEARNING EXPERIMENT")
print("FAILURE → LEARNING → RETRY → SUCCESS")
print("=" * 65)


# =========================================================
# CONTROLLED TOOL
# =========================================================

class ControlledCalculator:

    def __init__(self):
        self.attempts = 0

    def calculate(self, expression):

        self.attempts += 1

        print(
            f"\nCalculator attempt #{self.attempts}"
        )

        # -------------------------------------------------
        # DELIBERATE FIRST-ATTEMPT FAILURE
        # -------------------------------------------------

        if self.attempts == 1:

            print(
                "Tool result: FAILURE"
            )

            raise RuntimeError(
                "Simulated calculator failure"
            )

        # -------------------------------------------------
        # SECOND ATTEMPT SUCCEEDS
        # -------------------------------------------------

        result = 250 * 4

        print(
            "Tool result: SUCCESS"
        )

        return result


# =========================================================
# EXPERIMENT 1
# WITHOUT LEARNING
# =========================================================

print("\n" + "-" * 65)
print("EXPERIMENT 1 — WITHOUT LEARNING")
print("-" * 65)


calculator_without_learning = ControlledCalculator()

attempts_without_learning = 0

try:

    attempts_without_learning += 1

    result = calculator_without_learning.calculate(
        "250 * 4"
    )

    print(
        "Final result:",
        result
    )

except Exception as error:

    print(
        "Agent behavior: STOPPED after failure"
    )

    print(
        "Error:",
        error
    )


print(
    "\nAttempts without learning:",
    attempts_without_learning
)


# =========================================================
# STORE RECOVERY LESSON
# =========================================================

print("\n" + "-" * 65)
print("LEARNING FROM FAILURE")
print("-" * 65)


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


save_lesson(
    failed_task,
    failed_response,
    2,
    "NO",
    lesson_type,
    lesson
)


print(
    "Lesson learned:"
)

print(
    lesson
)


# =========================================================
# RETRIEVE LEARNING
# =========================================================

print("\n" + "-" * 65)
print("RETRIEVING LEARNED BEHAVIOR")
print("-" * 65)


lessons = get_lessons_by_type(
    "ERROR_RECOVERY",
    10
)


recovery_strategy = None


for lesson_record in lessons:

    stored_lesson = lesson_record[4]

    if "retry" in stored_lesson.lower():

        recovery_strategy = stored_lesson

        break


if recovery_strategy:

    print(
        "ERROR_RECOVERY strategy retrieved:"
    )

    print(
        recovery_strategy
    )

else:

    print(
        "No recovery strategy retrieved."
    )


# =========================================================
# EXPERIMENT 2
# WITH LEARNING
# =========================================================

print("\n" + "-" * 65)
print("EXPERIMENT 2 — WITH LEARNING")
print("-" * 65)


calculator_with_learning = ControlledCalculator()

attempts_with_learning = 0

max_retries = 2

while True:

    try:

        attempts_with_learning += 1

        result = calculator_with_learning.calculate(
            "250 * 4"
        )

        print(
            "\nAgent behavior: TASK RECOVERED"
        )

        print(
            "Final result:",
            result
        )

        break

    except Exception as error:

        print(
            "Observed failure:",
            error
        )

        # -------------------------------------------------
        # USE LEARNED RECOVERY STRATEGY
        # -------------------------------------------------

        if (
            recovery_strategy
            and "retry" in recovery_strategy.lower()
            and attempts_with_learning <= max_retries
        ):

            print(
                "Learned strategy activated: RETRY"
            )

            continue

        print(
            "Agent behavior: STOPPED"
        )

        break


# =========================================================
# FINAL COMPARISON
# =========================================================

print("\n" + "=" * 65)
print("FINAL EXPERIMENT RESULTS")
print("=" * 65)


print(
    "\nWITHOUT LEARNING"
)

print(
    "Attempts:",
    attempts_without_learning
)

print(
    "Outcome: FAILURE"
)


print(
    "\nWITH LEARNING"
)

print(
    "Attempts:",
    attempts_with_learning
)

print(
    "Outcome: SUCCESS"
)


print("\n" + "-" * 65)


if (
    attempts_without_learning == 1
    and attempts_with_learning == 2
):

    print(
        "BEHAVIORAL IMPROVEMENT: YES"
    )

    print(
        "The learned recovery strategy changed "
        "the agent's behavior."
    )

else:

    print(
        "BEHAVIORAL IMPROVEMENT: NO"
    )


print("=" * 65)