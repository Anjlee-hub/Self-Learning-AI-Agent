from agent_state import AgentState


goal = "Calculate 50 * 20 and get the current time"

plan = [
    "Calculate 50 * 20",
    "Get the current time"
]


state = AgentState(
    goal,
    plan
)


print("\n🧠 INITIAL STATE")
print(state.show_state())


state.start()

print("\n▶️ Starting agent...")
print(state.show_state())


state.complete_step(
    "Calculate 50 * 20",
    1000
)

print("\n✅ STEP 1 COMPLETED")
print(state.show_state())


state.complete_step(
    "Get the current time",
    "10:30 AM"
)

state.finish()

print("\n🏁 FINAL STATE")
print(state.show_state())