import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from agent_state import AgentState
from plan_executor import execute_plan


goal = (
    "Calculate 50 * 20, get the current time, "
    "and count the words in 'AI is amazing'"
)


plan = """
1. Calculate 50 * 20
2. Get the current time
3. Count the words in 'AI is amazing'
"""


# ==========================================
# CREATE STATE
# ==========================================

state = AgentState(
    goal,
    [
        "Calculate 50 * 20",
        "Get the current time",
        "Count the words in 'AI is amazing'"
    ]
)


print("\n🧠 INITIAL STATE")
print(state.show_state())


# ==========================================
# START AGENT
# ==========================================

state.start()


print("\n▶️ AGENT STARTED")
print(state.show_state())


# ==========================================
# EXECUTE PLAN
# ==========================================

results = execute_plan(
    plan,
    state
)


# ==========================================
# FINISH
# ==========================================

if state.status != "failed":

    state.finish()


print("\n📦 RESULTS")
print(results)


print("\n🏁 FINAL AGENT STATE")
print(state.show_state())