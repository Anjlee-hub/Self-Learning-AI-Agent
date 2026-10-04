import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from memory.memory import (
    init_db,
    save_lesson,
    get_lessons
)

from lesson_retriever import retrieve_similar_lessons
from learning import extract_learning_strategy


# =========================================================
# BEHAVIORAL LEARNING TEST
# =========================================================

print("=" * 70)
print("BEHAVIORAL LEARNING TEST")
print("=" * 70)

print("""
Goal:

FAILURE
   ↓
ERROR RECOVERY LESSON
   ↓
STORE IN MEMORY
   ↓
RETRIEVE LATER
   ↓
EXTRACT STRATEGY
   ↓
BEHAVIORAL CHANGE
""")


init_db()


# =========================================================
# STEP 1 — CREATE FAILURE EXPERIENCE
# =========================================================

print("\n" + "=" * 70)
print("STEP 1 — STORE FAILURE RECOVERY EXPERIENCE")
print("=" * 70)


failure_input = (
    "Calculate 500 * 8 using the calculator tool."
)

failure_response = (
    "Tool execution failed: calculator unavailable."
)

failure_lesson = (
    "Retry a failed tool operation before abandoning the task."
)

failure_type = "ERROR_RECOVERY"


save_lesson(
    failure_input,
    failure_response,
    1,
    "NO",
    failure_lesson,
    failure_type
)


print("\n❌ Previous experience:")
print(failure_response)

print("\n🧠 Learned lesson:")
print(failure_lesson)

print("\n💾 Failure recovery lesson stored.")


# =========================================================
# STEP 2 — RETRIEVE FOR NEW TASK
# =========================================================

print("\n" + "=" * 70)
print("STEP 2 — RETRIEVE LEARNING FOR NEW TASK")
print("=" * 70)


new_task = (
    "Calculate 750 * 6 using the calculator tool."
)


lessons = get_lessons()


retrieved = retrieve_similar_lessons(
    new_task,
    lessons,
    top_k=5
)


print("\nNew task:")
print(new_task)

print(
    f"\n🔎 Retrieved lessons: "
    f"{len(retrieved)}"
)


for index, lesson in enumerate(
    retrieved,
    1
):

    print(
        f"\nLesson {index}:"
    )

    print(
        f"Input: {lesson[0]}"
    )

    print(
        f"Lesson: {lesson[4]}"
    )

    print(
        f"Type: {lesson[5]}"
    )


# =========================================================
# STEP 3 — EXTRACT STRATEGY
# =========================================================

print("\n" + "=" * 70)
print("STEP 3 — EXTRACT LEARNED STRATEGY")
print("=" * 70)


if not retrieved:

    print(
        "\n❌ No relevant learning retrieved."
    )

    print(
        "\nBEHAVIORAL LEARNING TEST: FAIL"
    )

    sys.exit(1)


strategy = extract_learning_strategy(
    new_task,
    retrieved
)


print("\n🧠 Extracted strategy:")
print(strategy)


# =========================================================
# STEP 4 — VERIFY RECOVERY BEHAVIOR
# =========================================================

print("\n" + "=" * 70)
print("STEP 4 — VERIFY BEHAVIORAL STRATEGY")
print("=" * 70)


strategy_lower = (
    strategy.lower()
)


# ---------------------------------------------------------
# Recovery action
# ---------------------------------------------------------

retry_indicators = [

    "retry",

    "try again",

    "attempt again",

    "repeat",

    "re-execute",

    "execute again"
]


# ---------------------------------------------------------
# Failure / invalid-operation context
# ---------------------------------------------------------

failure_indicators = [

    "failed",

    "failure",

    "error",

    "invalid",

    "unsuccessful",

    "unsuccessfully",

    "does not work",

    "did not work",

    "not work",

    "wrong result",

    "incorrect result"
]


has_retry_behavior = any(

    word in strategy_lower

    for word in retry_indicators
)


has_failure_context = any(

    word in strategy_lower

    for word in failure_indicators
)


print(
    f"\nRetry behavior detected: "
    f"{has_retry_behavior}"
)

print(
    f"Failure/recovery context detected: "
    f"{has_failure_context}"
)


if (
    has_retry_behavior
    and has_failure_context
):

    print(
        "\n✅ Learned strategy contains "
        "failure-recovery behavior."
    )

else:

    print(
        "\n❌ Learned strategy does not contain "
        "the expected recovery behavior."
    )

    print(
        "\nBEHAVIORAL LEARNING TEST: FAIL"
    )

    sys.exit(1)


# =========================================================
# STEP 5 — FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("STEP 5 — RESULT")
print("=" * 70)

print("""
The agent successfully demonstrated:

1. A failure experience was stored.
2. The failure lesson was retrieved for a new task.
3. A reusable strategy was extracted.
4. The strategy contains recovery behavior.

Therefore:

EXPERIENCE
    ↓
MEMORY
    ↓
RETRIEVAL
    ↓
LEARNED STRATEGY
    ↓
RECOVERY BEHAVIOR

""")

print(
    "✅ BEHAVIORAL LEARNING PIPELINE: PASS"
)

print("=" * 70)