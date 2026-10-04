import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.lesson_deduplicator import (
    normalize_lesson,
    are_same_lesson,
    deduplicate_lessons
)


print("=" * 70)
print("LESSON DEDUPLICATION TEST")
print("=" * 70)


# ============================================================
# TEST 1 — SAME LESSON, DIFFERENT WORDING
# ============================================================

lesson_a = (
    "Retry a failed tool operation before abandoning the task."
)

lesson_b = (
    "Retry the Calculator tool when the first execution "
    "fails before reporting the operation as unsuccessful."
)

type_a = "ERROR_RECOVERY"
type_b = "ERROR_RECOVERY"


print("\nTEST 1 — Similar recovery lessons")

print("\nLesson A:")
print(lesson_a)

print("\nLesson B:")
print(lesson_b)

print("\nNormalized A:")
print(normalize_lesson(lesson_a))

print("\nNormalized B:")
print(normalize_lesson(lesson_b))

print(
    "\nAre same lesson:",
    are_same_lesson(
        lesson_a,
        type_a,
        lesson_b,
        type_b
    )
)


# ============================================================
# TEST 2 — DIFFERENT BEHAVIORS
# ============================================================

lesson_c = (
    "Retry a failed tool operation before abandoning the task."
)

lesson_d = (
    "Use the Calculator tool for arithmetic operations."
)

print("\n" + "=" * 70)
print("TEST 2 — Different behaviors")
print("=" * 70)

print("\nLesson C:")
print(lesson_c)

print("\nLesson D:")
print(lesson_d)

print(
    "\nAre same lesson:",
    are_same_lesson(
        lesson_c,
        "ERROR_RECOVERY",
        lesson_d,
        "TOOL_USAGE"
    )
)


# ============================================================
# TEST 3 — DUPLICATE LIST
# ============================================================

test_lessons = [

    (
        "Calculate 250 * 4.",
        "Tool failed.",
        1,
        "NO",
        "Retry a failed tool operation before abandoning the task.",
        "ERROR_RECOVERY"
    ),

    (
        "Calculate 250 * 4 using the Calculator tool",
        "Calculator failed.",
        2,
        "NO",
        "Retry the Calculator tool when the first execution "
        "fails before reporting the operation as unsuccessful.",
        "ERROR_RECOVERY"
    ),

    (
        "Calculate 20 * 5",
        "Success.",
        5,
        "YES",
        "Use the Calculator tool for arithmetic operations.",
        "TOOL_USAGE"
    ),

    (
        "Calculate 18 * 7",
        "Success.",
        5,
        "YES",
        "Use the Calculator tool for arithmetic operations.",
        "TOOL_USAGE"
    )
]


print("\n" + "=" * 70)
print("TEST 3 — DEDUPLICATING A LESSON LIST")
print("=" * 70)

print("\nOriginal lessons:", len(test_lessons))

unique_lessons = deduplicate_lessons(test_lessons)

print("Unique lessons:", len(unique_lessons))

print("\nRemaining lessons:")

for index, lesson in enumerate(unique_lessons, 1):

    print(f"\n{index}.")
    print("Task:", lesson[0])
    print("Lesson:", lesson[4])
    print("Type:", lesson[5])


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)


test_1 = are_same_lesson(
    lesson_a,
    type_a,
    lesson_b,
    type_b
)

test_2 = not are_same_lesson(
    lesson_c,
    "ERROR_RECOVERY",
    lesson_d,
    "TOOL_USAGE"
)

test_3 = len(unique_lessons) < len(test_lessons)


if test_1 and test_2 and test_3:

    print("""
✅ LESSON DEDUPLICATION: PASS

Confirmed:

1. Equivalent recovery lessons are recognized.
2. Different behavioral lessons are preserved.
3. Duplicate lessons are removed.
4. Different lesson types remain distinct.
""")

else:

    print("""
❌ LESSON DEDUPLICATION: FAIL

The deduplication logic needs further correction.
""")


print("=" * 70)