import sys
import os

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


# =========================================================
# IMPORTS
# =========================================================

from agent_loop import run_agent


# =========================================================
# TEST
# =========================================================

print("\n" + "=" * 70)
print("REAL AGENT LEARNING INTEGRATION TEST")
print("=" * 70)

print("""
This test checks the actual run_agent() pipeline.

Goal:

REAL AGENT
    ↓
failure/recovery experience
    ↓
learning
    ↓
future retrieval
""")

print("\n" + "=" * 70)
print("TEST TASK")
print("=" * 70)

user_input = (
    "Calculate 250 * 4 and get the current time."
)

print("\nUser:")
print(user_input)


# =========================================================
# RUN ACTUAL AGENT
# =========================================================

print("\n" + "=" * 70)
print("RUNNING ACTUAL AGENT")
print("=" * 70)

try:

    result = run_agent(user_input)

    print("\n" + "=" * 70)
    print("AGENT RESULT")
    print("=" * 70)

    print(result)

except Exception as error:

    print("\n" + "=" * 70)
    print("AGENT EXECUTION ERROR")
    print("=" * 70)

    print(type(error).__name__)
    print(error)

    print("\n❌ REAL AGENT TEST FAILED.")

    sys.exit(1)


# =========================================================
# FINAL CHECK
# =========================================================

print("\n" + "=" * 70)
print("REAL AGENT TEST COMPLETED")
print("=" * 70)

print("""
The actual run_agent() function executed.

Now inspect the output above for:

1. Retrieved learning
2. Planning
3. Tool execution
4. Evaluation
5. Learning validation
6. Lesson storage
7. Final response
""")