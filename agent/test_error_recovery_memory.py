import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from memory.memory import init_db, get_lessons_by_type


print("=" * 70)
print("ERROR RECOVERY MEMORY TEST")
print("=" * 70)

init_db()

print("\n🔎 Retrieving ERROR_RECOVERY lessons...")

lessons = get_lessons_by_type("ERROR_RECOVERY")

print(f"\nERROR_RECOVERY lessons found: {len(lessons)}")


print("\n" + "=" * 70)
print("RETRIEVED LEARNING")
print("=" * 70)

found_recovery_lesson = False

for index, row in enumerate(lessons, 1):

    if len(row) != 6:
        continue

    user_input = row[0]
    agent_response = row[1]
    score = row[2]
    success = row[3]
    lesson = row[4]
    lesson_type = row[5]

    print(f"\nLesson {index}")
    print("-" * 70)
    print("Task:", user_input)
    print("Score:", score)
    print("Success:", success)
    print("Lesson:", lesson)
    print("Type:", lesson_type)

    if lesson_type == "ERROR_RECOVERY":

        recovery_keywords = [
            "retry",
            "failed",
            "failure",
            "recover"
        ]

        lesson_lower = lesson.lower()

        if any(
            keyword in lesson_lower
            for keyword in recovery_keywords
        ):
            found_recovery_lesson = True


print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)

if found_recovery_lesson:

    print("""
✅ ERROR RECOVERY MEMORY: PASS

Confirmed:

1. ERROR_RECOVERY experiences exist in SQLite.
2. The lessons can be retrieved by lesson type.
3. Retrieved lessons contain reusable recovery behavior.
4. The ERROR_RECOVERY memory layer is functioning.
""")

else:

    print("""
❌ ERROR RECOVERY MEMORY: FAIL

No reusable ERROR_RECOVERY lesson was retrieved.
""")

print("=" * 70)