import sys
import os

# =========================================================
# PROJECT PATH
# =========================================================

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# =========================================================
# IMPORTS
# =========================================================

from memory.memory import (
    init_db,
    get_lessons
)

from lesson_retriever import (
    retrieve_similar_lessons
)

from learning import (
    extract_learning_strategy
)

from planner import (
    create_plan
)


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# TEST TASK
# =========================================================

TEST_TASK = (
    "Calculate 40 * 8, get the current time, "
    "and count the words in 'Self learning AI agent'"
)


# =========================================================
# RETRIEVE LEARNING
# =========================================================

def get_learning_for_task(task):

    lessons = get_lessons()

    if not lessons:

        return "", []

    similar_lessons = retrieve_similar_lessons(
        task,
        lessons,
        top_k=5
    )

    if not similar_lessons:

        return "", []

    strategy = extract_learning_strategy(
        task,
        similar_lessons
    )

    return strategy, similar_lessons


# =========================================================
# START EXPERIMENT
# =========================================================

print("\n🧪 LEARNING IMPACT EXPERIMENT")
print("=" * 60)

print("\n🎯 TEST TASK")
print("-" * 60)

print(TEST_TASK)


# =========================================================
# EXPERIMENT 1 — WITHOUT LEARNING
# =========================================================

print("\n\n🔵 EXPERIMENT 1 — WITHOUT LEARNING")
print("=" * 60)

plan_without_learning = create_plan(
    TEST_TASK,
    ""
)

print("\n📋 PLAN WITHOUT LEARNING")
print("-" * 60)

print(plan_without_learning)


# =========================================================
# RETRIEVE PREVIOUS LEARNING
# =========================================================

print("\n\n📚 RETRIEVING PREVIOUS EXPERIENCE")
print("=" * 60)

learning_strategy, similar_lessons = (
    get_learning_for_task(
        TEST_TASK
    )
)


# =========================================================
# SHOW RETRIEVED LESSONS
# =========================================================

print("\n🔎 RETRIEVED LESSONS")
print("-" * 60)

if not similar_lessons:

    print("No relevant lessons found.")

else:

    for index, lesson in enumerate(
        similar_lessons,
        start=1
    ):

        print(
            f"\n{index}. Previous task:"
        )

        print(
            lesson[0]
        )

        print(
            f"Lesson type: {lesson[5]}"
        )

        print(
            f"Lesson: {lesson[4]}"
        )


# =========================================================
# SHOW LEARNED STRATEGY
# =========================================================

print("\n\n🧠 EXTRACTED LEARNING")
print("=" * 60)

if learning_strategy:

    print(
        learning_strategy
    )

else:

    print(
        "NO_USEFUL_LEARNING"
    )


# =========================================================
# EXPERIMENT 2 — WITH LEARNING
# =========================================================

print("\n\n🟢 EXPERIMENT 2 — WITH LEARNING")
print("=" * 60)

plan_with_learning = create_plan(
    TEST_TASK,
    learning_strategy
)

print("\n📋 PLAN WITH LEARNING")
print("-" * 60)

print(
    plan_with_learning
)


# =========================================================
# ANALYSIS
# =========================================================

print("\n\n📊 EXPERIMENT ANALYSIS")
print("=" * 60)

print(
    f"Retrieved lessons: "
    f"{len(similar_lessons)}"
)

print(
    f"Learning retrieved: "
    f"{'YES' if learning_strategy else 'NO'}"
)


# =========================================================
# CHECK WHETHER LEARNING IS RELEVANT
# =========================================================

relevant_learning = False

if learning_strategy:

    strategy_lower = (
        learning_strategy.lower()
    )

    relevant_keywords = [
        "calculator",
        "word counter",
        "tool",
        "verify",
        "planning",
        "separate",
        "step"
    ]

    for keyword in relevant_keywords:

        if keyword in strategy_lower:

            relevant_learning = True
            break


print(
    f"Learning appears task-relevant: "
    f"{'YES' if relevant_learning else 'NO'}"
)


# =========================================================
# PLAN COMPARISON
# =========================================================

print("\n🔬 PLAN COMPARISON")
print("-" * 60)

if plan_without_learning == plan_with_learning:

    print(
        "Plans are identical."
    )

    print(
        "This does NOT automatically mean learning failed."
    )

    print(
        "The planner may already have produced the correct "
        "plan without needing additional advice."
    )

else:

    print(
        "Plans are different."
    )

    print(
        "The learned strategy changed the planner output."
    )


# =========================================================
# FINAL INTERPRETATION
# =========================================================

print("\n\n🧠 EXPERIMENT CONCLUSION")
print("=" * 60)

if (
    learning_strategy
    and relevant_learning
):

    print(
        "✅ Relevant previous knowledge was retrieved "
        "and converted into a task-relevant strategy."
    )

else:

    print(
        "⚠️ No clearly relevant learning strategy "
        "was produced."
    )

print(
    "\nImportant:"
)

print(
    "A changed plan is NOT required to prove retrieval."
)

print(
    "The next experiment will test whether learned "
    "knowledge can improve an actual agent decision "
    "or recovery behavior."
)