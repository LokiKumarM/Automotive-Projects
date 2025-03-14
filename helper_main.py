from helper_submain import *

def feedback_loop(context: str, evaluator_prompt: str, generator_prompt: str):
    """Keep generating and evaluating until requirements are met."""
    chain_of_thought = ""

    test_cases = generate_test_case(context, generator_prompt)
    feedback = ""

    max_iteration = 4
    for i in range(max_iteration):
        # print(f"\n========================= iteration for evaluation {i+1} ==========================\n")
        evaluation, feedback = evaluate_test_case(context, evaluator_prompt, test_cases, feedback=feedback)
        if evaluation.strip() == "PASS":
            test_cases = [iterator_str.strip() for iterator_str in test_cases.split("\n\n") if iterator_str.strip()]
            return test_cases

        test_cases = generate_test_case(context, generator_prompt, feedback=feedback)
        chain_of_thought = [iterator_str.strip() for iterator_str in test_cases.split("\n\n") if iterator_str.strip()]
    return chain_of_thought