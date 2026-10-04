from agent_state import AgentState
from plan_executor import execute_plan


plan = """
1. Multiply 12 by 8
2. Add 10 and 20
3. Subtract 5 from 30
4. Divide 20 by 4
"""

state = AgentState(
    "Test plan execution",
    [
        "Multiply 12 by 8",
        "Add 10 and 20",
        "Subtract 5 from 30",
        "Divide 20 by 4",
    ],
)

results = execute_plan(plan, state)

print("\n📦 FINAL RESULTS")
print("=" * 50)
print(results)