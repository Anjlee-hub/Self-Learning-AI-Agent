from agent_state import AgentState


state = AgentState(
    "Test recovery",
    ["Temporary failure", "Successful step"]
)

state.start()

print("\n🧠 START")
print(state.show_state())


# Simulate failure
state.fail("Temporary tool error")

print("\n❌ FAILURE")
print(state.show_state())


# Retry
if state.retry():

    print("\n🔄 RETRY SUCCESSFULLY ALLOWED")

    state.complete_step(
        "Temporary failure",
        "Recovered successfully"
    )


state.finish()


print("\n🏁 RECOVERED")
print(state.show_state())