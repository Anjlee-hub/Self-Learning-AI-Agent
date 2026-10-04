from evaluator import evaluate_response


user_input = "What is 25 * 40?"

agent_response = "The answer is 1000."

result = evaluate_response(
    user_input,
    agent_response
)

print("\nEvaluation:")
print(result)