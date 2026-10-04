import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from memory.memory import init_db, get_lessons
from lesson_retriever import (
    retrieve_similar_lessons,
    get_preferred_lesson_types
)
from task_features import extract_task_features


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# CURRENT NEW TASK
# =========================================================

current_task = (
    "Calculate 25 * 40, get the current time, "
    "and count the words in 'I am learning AI'"
)


# =========================================================
# SHOW CURRENT TASK FEATURES
# =========================================================

print("\n🔎 CURRENT TASK FEATURES")
print("=" * 50)

features = extract_task_features(
    current_task
)

print(features)


# =========================================================
# SHOW PREFERRED LESSON TYPES
# =========================================================

print("\n🧩 PREFERRED LESSON TYPES")
print("=" * 50)

preferred_types = get_preferred_lesson_types(
    current_task
)

if preferred_types:

    for lesson_type in preferred_types:
        print(f"• {lesson_type}")

else:

    print("No specific lesson types detected.")


# =========================================================
# LOAD PREVIOUS LESSONS
# =========================================================

lessons = get_lessons()

print("\n📚 TOTAL STORED LESSONS")
print("=" * 50)

print(
    f"Total lessons in database: {len(lessons)}"
)


# =========================================================
# RETRIEVE SIMILAR EXPERIENCES
# =========================================================

similar_lessons = retrieve_similar_lessons(
    current_task,
    lessons,
    top_k=5
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\n🧠 SIMILAR PREVIOUS EXPERIENCES")
print("=" * 50)

if not similar_lessons:

    print("No similar lessons found.")

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
            f"Score: {lesson[2]}/5"
        )

        print(
            f"Success: {lesson[3]}"
        )

        print(
            f"Lesson type: {lesson[5]}"
        )

        print(
            f"Lesson: {lesson[4]}"
        )

        print(
            "-" * 50
        )


# =========================================================
# SUMMARY
# =========================================================

print("\n📊 RETRIEVAL SUMMARY")
print("=" * 50)

print(
    f"Current task features: {features}"
)

print(
    f"Preferred lesson types: {preferred_types}"
)

print(
    f"Retrieved lessons: {len(similar_lessons)}"
)