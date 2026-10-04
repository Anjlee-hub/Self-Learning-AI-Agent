from planner import create_plan


user_input = (
    "Calculate 25 * 40, get the current time, "
    "and count the words in 'I am learning AI'"
)

learned_strategy = (
    "LEARNED_STRATEGY: "
    "Execute each independent operation separately."
)


plan = create_plan(
    user_input,
    learned_strategy
)


print("\n🧠 LEARNING-GUIDED PLAN")
print("=" * 45)

print(plan)