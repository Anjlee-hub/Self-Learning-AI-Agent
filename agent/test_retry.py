from agent_state import AgentState


state = AgentState(
    "Test retry system",
    ["Test a failing step"]
)


print("\n🧠 INITIAL STATE")
print(state.show_state())


state.start()

print("\n▶️ AGENT STARTED")
print(state.show_state())


state.fail("Test error")

print("\n❌ STEP FAILED")
print(state.show_state())


print("\n🔄 RETRYING...")

if state.retry():

    print("Retry allowed!")
    print(state.show_state())

else:

    print("Retry limit reached!")


print("\n🔄 SECOND RETRY...")

if state.retry():

    print("Retry allowed!")
    print(state.show_state())

else:

    print("Retry limit reached!")


print("\n🔄 THIRD RETRY...")

if state.retry():

    print("Retry allowed!")
    print(state.show_state())

else:

    print("Retry limit reached!")


print("\n🏁 FINAL STATE")
print(state.show_state())