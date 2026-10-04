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

from memory.memory import (
    init_db,
    get_lessons
)

from lesson_quality import is_useful_lesson
from lesson_deduplicator import deduplicate_lessons


# ==================================================
# INITIALIZE DATABASE
# ==================================================

init_db()


# ==================================================
# LOAD LESSONS
# ==================================================

lessons = get_lessons()


print("\n📚 TOTAL STORED LESSONS")
print("=" * 45)

print(
    len(lessons)
)


# ==================================================
# QUALITY FILTERING
# ==================================================

useful_lessons = []

for lesson in lessons:

    useful = is_useful_lesson(
        lesson[0],
        lesson[1],
        lesson[2],
        lesson[3],
        lesson[4]
    )

    if useful:

        useful_lessons.append(
            lesson
        )


print("\n🧠 USEFUL LESSONS")
print("=" * 45)

print(
    len(useful_lessons)
)


# ==================================================
# DEDUPLICATION
# ==================================================

unique_lessons = deduplicate_lessons(
    useful_lessons
)


print("\n🧹 UNIQUE LESSON TYPES")
print("=" * 45)

print(
    len(unique_lessons)
)


# ==================================================
# DISPLAY RESULTS
# ==================================================

for index, lesson in enumerate(
    unique_lessons,
    start=1
):

    print(
        f"\n{index}. Task:"
    )

    print(
        lesson[0]
    )

    print(
        f"Score: {lesson[2]}/5"
    )

    print(
        f"Lesson: {lesson[4]}"
    )