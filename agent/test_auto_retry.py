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


state = AgentState(
    "Test automatic retry",
    ["Unknown operation"]
)

state.start()

print("\n🧠 INITIAL STATE")
print(state.show_state())


results = execute_plan(
    "1. Do something impossible",
    state
)


print("\n📦 RESULTS")
print(results)


print("\n🏁 FINAL STATE")
print(state.show_state())