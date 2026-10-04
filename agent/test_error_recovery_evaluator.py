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

from evaluator import evaluate_response


# =========================================================
# SIMULATED FAILED EXECUTION
# =========================================================

user_input = """
Calculate 250 * 4.
"""

agent_response = """
The calculator tool failed while executing the calculation.
The operation could not be completed.
"""

print("\n" + "=" * 60)
print("ERROR RECOVERY EVALUATOR TEST")
print("=" * 60)

print("\nUser request:")
print(user_input)

print("Agent response:")
print(agent_response)


# =========================================================
# EVALUATE
# =========================================================

score, success, lesson_type, lesson = evaluate_response(
    user_input,
    agent_response
)


# =========================================================
# RESULTS
# =========================================================

print("\n" + "=" * 60)
print("EVALUATOR RESULT")
print("=" * 60)

print("\nScore:", score)
print("Success:", success)
print("Lesson type:", lesson_type)
print("Lesson:", lesson)


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 60)
print("TEST RESULT")
print("=" * 60)

if (
    success == "NO"
    and lesson_type == "ERROR_RECOVERY"
    and lesson
    and "retry" in lesson.lower()
):

    print("\n✅ ERROR RECOVERY LEARNING: PASS")
    print("The evaluator generated a reusable retry strategy.")

else:

    print("\n❌ ERROR RECOVERY LEARNING: FAIL")
    print("The evaluator did not generate the expected recovery lesson.")