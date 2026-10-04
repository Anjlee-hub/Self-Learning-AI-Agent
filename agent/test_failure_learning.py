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
# IMPORT PROJECT MODULES
# =========================================================

from memory.memory import (
    init_db,
    save_lesson,
    get_lessons_by_type
)

from agent.lesson_retriever import retrieve_similar_lessons
from agent.learning import extract_learning_strategy


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


print("\n" + "=" * 60)
print("FAILURE → LEARNING → RECOVERY EXPERIMENT")
print("=" * 60)


# =========================================================
# STEP 1 — SIMULATE FAILURE
# =========================================================

failed_task = (
    "Calculate 125 * 8 using the Calculator tool"
)

failed_response = (
    "The Calculator tool failed because the first "
    "execution attempt produced an invalid result."
)

print("\n[1] SIMULATED FAILURE")
print("Task:", failed_task)
print("Failure:", failed_response)


# =========================================================
# STEP 2 — CREATE LESSON
# =========================================================

lesson_type = "ERROR_RECOVERY"

lesson = (
    "Retry the Calculator tool when the first execution "
    "fails before reporting the operation as unsuccessful."
)

print("\n[2] GENERATED LESSON")
print("Lesson type:", lesson_type)
print("Lesson:", lesson)


# =========================================================
# STEP 3 — STORE LESSON
# =========================================================

save_lesson(
    failed_task,
    failed_response,
    2,
    "NO",
    lesson_type,
    lesson
)

print("\n[3] LESSON STORED")
print("ERROR_RECOVERY lesson saved to memory.")


# =========================================================
# STEP 4 — RETRIEVE SIMILAR LESSON
# =========================================================

future_task = (
    "Compute 250 * 4 using the Calculator tool. "
    "The Calculator may fail during execution."
)

print("\n[4] FUTURE SIMILAR TASK")
print(future_task)


# Existing retriever API:
# retrieve_similar_lessons(user_input, lessons, top_k=...)
#
# First obtain ERROR_RECOVERY lessons.

error_recovery_lessons = get_lessons_by_type(
    "ERROR_RECOVERY",
    10
)


retrieved = retrieve_similar_lessons(
    future_task,
    error_recovery_lessons,
    5
)


print("\nRETRIEVED LESSONS:")


if not retrieved:

    print("No lessons retrieved.")

else:

    for index, item in enumerate(
        retrieved,
        start=1
    ):

        print(f"\n{index}.")

        print(
            "Task:",
            item[0]
        )

        print(
            "Score:",
            item[2]
        )

        print(
            "Success:",
            item[3]
        )

        print(
            "Lesson:",
            item[4]
        )

        print(
            "Lesson type:",
            item[5]
        )


# =========================================================
# STEP 5 — EXTRACT LEARNING
# =========================================================

strategy = extract_learning_strategy(
    future_task,
    retrieved
)


print("\n[5] LEARNED STRATEGY")
print(strategy)


# =========================================================
# FINAL VERIFICATION
# =========================================================

print("\n" + "=" * 60)
print("EXPERIMENT RESULT")
print("=" * 60)


print(
    "\nERROR_RECOVERY lessons in database:",
    len(error_recovery_lessons)
)


if retrieved:

    print(
        "Learning retrieved: YES"
    )

else:

    print(
        "Learning retrieved: NO"
    )


if "retry" in strategy.lower():

    print(
        "Recovery strategy learned: YES"
    )

else:

    print(
        "Recovery strategy learned: NO"
    )


print("\n" + "=" * 60)