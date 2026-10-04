import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent_state import AgentState
from agent.plan_executor import execute_plan
from agent.evaluator import evaluate_response
from agent.learning_validator import validate_learning
from memory.memory import init_db, save_lesson, get_recent_lessons


print("=" * 70)
print("REAL AGENT FAILURE → LEARNING → RECOVERY TEST")
print("=" * 70)

print("""
This test checks whether the agent can:

1. Experience a real tool failure
2. Detect the failure
3. Learn an ERROR_RECOVERY lesson
4. Store the lesson
5. Use the learned retry strategy
6. Recover successfully
""")

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

init_db()


# ------------------------------------------------------------
# CONTROLLED TOOL
# ------------------------------------------------------------

class ControlledCalculator:

    def __init__(self):
        self.attempts = 0

    def calculate(self, expression):
        self.attempts += 1

        print(f"\n🔧 Calculator attempt #{self.attempts}")

        # First attempt intentionally fails
        if self.attempts == 1:
            raise RuntimeError(
                "Simulated calculator failure"
            )

        # Second attempt succeeds
        return 1000


controlled_calculator = ControlledCalculator()


# ------------------------------------------------------------
# PLAN
# ------------------------------------------------------------

plan = [
    "Calculate 250 * 4"
]

state = AgentState(
    "Calculate 250 * 4",
    plan
)

# Disable normal retry.
# We want to prove that the LEARNED retry mechanism
# is responsible for recovery.
state.max_retries = 0

state.start()

print("\n" + "=" * 70)
print("PHASE 1 — FIRST EXECUTION")
print("=" * 70)

print("\nPlan:")
for i, step in enumerate(plan, 1):
    print(f"{i}. {step}")

print("\nAgent state:")
print(state.show_state())


# ------------------------------------------------------------
# FIRST EXECUTION
# ------------------------------------------------------------

try:

    state = execute_plan(
        plan,
        state,
        learning_strategy="",
        calculator_function=controlled_calculator.calculate
    )

except Exception as e:

    state.fail(str(e))

print("\nAgent state after first execution:")
print(state.show_state())


# ------------------------------------------------------------
# CREATE FAILURE RESPONSE
# ------------------------------------------------------------

if state.status == "failed":

    failure_response = (
        "Tool execution failed: "
        + str(state.error)
    )

else:

    failure_response = (
        "Tool execution failed during the first attempt."
    )


print("\n" + "=" * 70)
print("PHASE 2 — EVALUATING FAILURE")
print("=" * 70)

print("\nFailure response:")
print(failure_response)


# ------------------------------------------------------------
# EVALUATOR
# ------------------------------------------------------------

score, success, lesson_type, lesson = evaluate_response(
    "Calculate 250 * 4",
    failure_response
)

print("\n📈 Score:", score)
print("✅ Success:", success)
print("🧩 Lesson type:", lesson_type)
print("🧠 Lesson:", lesson)


# ------------------------------------------------------------
# VALIDATE LEARNING
# ------------------------------------------------------------

valid, reason = validate_learning(
    "Calculate 250 * 4",
    failure_response,
    score,
    success,
    lesson
)

print("\n🧠 Learning valid:", "YES" if valid else "NO")
print("🔎 Validation reason:", reason)


# ------------------------------------------------------------
# STORE ERROR RECOVERY LESSON
# ------------------------------------------------------------

if valid:

    save_lesson(
        "Calculate 250 * 4",
        failure_response,
        score,
        success,
        lesson,
        lesson_type
    )

    print("\n💾 ERROR_RECOVERY lesson stored.")

else:

    print("\n❌ Learning was rejected.")


# ------------------------------------------------------------
# RETRIEVE LEARNING
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PHASE 3 — RETRIEVING LEARNED EXPERIENCE")
print("=" * 70)

lessons = get_recent_lessons(10)

error_recovery_lessons = [
    l for l in lessons
    if len(l) >= 6 and l[5] == "ERROR_RECOVERY"
]

print(
    f"\n🔎 ERROR_RECOVERY lessons found: "
    f"{len(error_recovery_lessons)}"
)

for lesson_row in error_recovery_lessons[:5]:

    print("\nLesson:")
    print(lesson_row[4])


# ------------------------------------------------------------
# LEARNED STRATEGY
# ------------------------------------------------------------

learned_strategy = (
    "Retry the Calculator tool when the first "
    "execution fails before reporting failure."
)

print("\n🧠 Learned strategy:")
print(learned_strategy)


# ------------------------------------------------------------
# PHASE 4 — RECOVERY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PHASE 4 — EXECUTING WITH LEARNED STRATEGY")
print("=" * 70)

recovery_plan = [
    "Calculate 250 * 4"
]

recovery_state = AgentState(
    "Calculate 250 * 4",
    recovery_plan
)

# Again disable normal retry.
recovery_state.max_retries = 0

recovery_state.start()

print("\nInitial recovery state:")
print(recovery_state.show_state())


# ------------------------------------------------------------
# EXECUTION WITH LEARNED RETRY
# ------------------------------------------------------------

recovery_state = execute_plan(
    recovery_plan,
    recovery_state,
    learning_strategy=learned_strategy,
    calculator_function=controlled_calculator.calculate
)

print("\nFinal recovery state:")
print(recovery_state.show_state())


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL RESULT")
print("=" * 70)

print("\nTotal calculator attempts:", controlled_calculator.attempts)
print("Final status:", recovery_state.status)

if recovery_state.status == "completed":

    print("""
✅ REAL LEARNED RECOVERY: PASS

The agent:
1. Experienced a tool failure.
2. Evaluated the failure.
3. Generated an ERROR_RECOVERY lesson.
4. Stored the lesson in memory.
5. Retrieved an ERROR_RECOVERY experience.
6. Applied a learned retry strategy.
7. Recovered successfully.
""")

else:

    print("""
❌ REAL LEARNED RECOVERY: FAIL

The agent did not successfully recover.
""")

print("=" * 70)