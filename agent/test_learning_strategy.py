from learning import extract_learning_strategy


lessons = [
    (
        "Calculate 50 * 20, get the current time, and count words",
        "The agent completed all three operations correctly.",
        5,
        "YES",
        "For multi-step requests, execute each independent operation separately."
    )
]


strategy = extract_learning_strategy(
    "Calculate 25 * 10, get the current time, and count the words in 'Hello AI'",
    lessons
)


print("\n🧠 LEARNED STRATEGY")
print("=" * 40)
print(strategy)