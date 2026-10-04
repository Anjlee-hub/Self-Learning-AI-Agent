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
from agent_state import AgentState
from plan_executor import execute_plan


# =========================================================
# FULL SELF-LEARNING LOOP TEST
# =========================================================

print("=" * 70)
print("FULL SELF-LEARNING LOOP TEST")
print("=" * 70)

print("""
PHASE 1
-------
Failure experience
      ↓
ERROR_RECOVERY lesson
      ↓
Memory


PHASE 2
-------
New task
      ↓
Retrieve lesson
      ↓
Extract strategy
      ↓
Executor
      ↓
Failure
      ↓
Automatic retry
      ↓
Success
""")


init_db()


# =========================================================
# PHASE 1 — LEARN FROM FAILURE
# =========================================================

print("\n" + "=" * 70)
print("PHASE 1 — LEARNING FROM FAILURE")
print("=" * 70)


failure_input = (
    "Calculate 900 * 7 using the calculator tool."
)

failure_response = (
    "Tool execution failed: calculator unavailable."
)

failure_lesson = (
    "Retry the calculator tool when the first "
    "execution fails before abandoning the task."
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


print("\n❌ Failure experience:")
print(failure_response)

print("\n🧠 Lesson learned:")
print(failure_lesson)

print("\n💾 ERROR_RECOVERY lesson stored.")


# =========================================================
# PHASE 2 — NEW TASK
# =========================================================

print("\n" + "=" * 70)
print("PHASE 2 — NEW TASK")
print("=" * 70)


new_task = (
    "Calculate 600 * 9 using the calculator tool."
)


print("\nNew task:")
print(new_task)


# =========================================================
# RETRIEVE LEARNING
# =========================================================

print("\n" + "=" * 70)
print("RETRIEVING PREVIOUS EXPERIENCE")
print("=" * 70)


lessons = get_lessons()


retrieved = retrieve_similar_lessons(
    new_task,
    lessons,
    top_k=5
)


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
# EXTRACT STRATEGY
# =========================================================

print("\n" + "=" * 70)
print("EXTRACTING LEARNED STRATEGY")
print("=" * 70)


if not retrieved:

    print(
        "\n❌ No previous learning retrieved."
    )

    print(
        "\nFULL SELF-LEARNING LOOP: FAIL"
    )

    sys.exit(1)


strategy = extract_learning_strategy(
    new_task,
    retrieved
)


print("\n🧠 Learned strategy:")
print(strategy)


strategy_lower = strategy.lower()


retry_indicators = [
    "retry",
    "try again",
    "attempt again",
    "repeat",
    "re-execute",
    "execute again"
]


has_retry_strategy = any(
    word in strategy_lower
    for word in retry_indicators
)


if not has_retry_strategy:

    print(
        "\n❌ No retry behavior extracted."
    )

    print(
        "\nFULL SELF-LEARNING LOOP: FAIL"
    )

    sys.exit(1)


print(
    "\n✅ Recovery strategy successfully retrieved."
)


# =========================================================
# CONTROLLED FAILURE TOOL
# =========================================================

print("\n" + "=" * 70)
print("EXECUTING NEW TASK WITH LEARNED STRATEGY")
print("=" * 70)


attempts = {
    "count": 0
}


def simulated_calculator(expression):

    attempts["count"] += 1

    print(
        f"\n🔧 Calculator attempt "
        f"{attempts['count']}"
    )


    # First attempt fails
    if attempts["count"] == 1:

        raise RuntimeError(
            "Simulated calculator failure"
        )


    # Second attempt succeeds
    return 5400


# =========================================================
# CREATE STATE
# =========================================================

plan = [
    "Calculate 600 * 9"
]


state = AgentState(
    new_task,
    plan
)


state.start()


print("\nInitial agent state:")
print(
    state.show_state()
)


# =========================================================
# EXECUTE WITH LEARNING
# =========================================================

final_state = execute_plan(

    plan,

    state,

    learning_strategy=strategy,

    calculator_function=simulated_calculator
)


# =========================================================
# VERIFY
# =========================================================

print("\n" + "=" * 70)
print("VERIFYING LEARNED BEHAVIOR")
print("=" * 70)


print("\nFinal agent state:")
print(
    final_state.show_state()
)


print(
    f"\nTotal calculator attempts: "
    f"{attempts['count']}"
)


# =========================================================
# FINAL CHECKS
# =========================================================

retry_happened = (
    attempts["count"] >= 2
)

task_completed = (
    final_state.status == "completed"
)

correct_result = (
    final_state.results == [5400]
)


print(
    f"\nRetry happened: "
    f"{retry_happened}"
)

print(
    f"Task completed: "
    f"{task_completed}"
)

print(
    f"Correct result: "
    f"{correct_result}"
)


# =========================================================
# FINAL RESULT
# =========================================================

if (
    retry_happened
    and task_completed
    and correct_result
):

    print("""
======================================================================
🔥 FULL SELF-LEARNING LOOP: PASS
======================================================================

The system demonstrated:

1. Failure experience
2. ERROR_RECOVERY learning
3. Memory storage
4. Relevant lesson retrieval
5. Learned strategy extraction
6. Strategy-driven executor behavior
7. Automatic retry
8. Successful recovery

FULL LOOP:

FAILURE
   ↓
LEARNING
   ↓
MEMORY
   ↓
RETRIEVAL
   ↓
STRATEGY
   ↓
BEHAVIOR CHANGE
   ↓
RECOVERY
   ↓
SUCCESS

======================================================================
""")

else:

    print("""
======================================================================
❌ FULL SELF-LEARNING LOOP: FAIL
======================================================================
""")

    sys.exit(1)