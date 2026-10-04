from agent.plan_executor import execute_plan
from agent.agent_state import AgentState


# =========================================================
# CONTROLLED FAILING CALCULATOR
# =========================================================

calls = {
    "count": 0
}


def fake_calculator(expression):
    calls["count"] += 1

    print(
        f"FAKE CALCULATOR ATTEMPT: {calls['count']}"
    )

    # First attempt intentionally fails
    if calls["count"] == 1:
        raise RuntimeError(
            "Controlled calculator failure"
        )

    # Second attempt succeeds
    return 20


# =========================================================
# TEST
# =========================================================

state = AgentState(
    "Test learned retry"
)

plan = [
    "Calculate 10 * 2"
]

learning_strategy = (
    "LEARNED_STRATEGY: "
    "Retry a failed tool operation "
    "before abandoning the task."
)


result = execute_plan(
    plan,
    state,
    learning_strategy=learning_strategy,
    calculator_function=fake_calculator
)


print()
print("=" * 60)
print("FINAL STATE")
print("=" * 60)

print(
    state.show_state()
)

print()
print(
    "TOTAL CALCULATOR CALLS:",
    calls["count"]
)