from orchestrator import *
from langchain.chains import ConversationChain
import streamlit as st

load_dotenv()

unpack={}

llm_generator = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

llm_eval = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def _format_prompt_worker(template: str,  **kwargs) -> str:
    """Format a prompt template with variables."""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required prompt variable: {e}")

def generate_test_case(context: str, prompt: str, feedback: str = ""):
    #full_prompt = f"{prompt}\n{feedback}\n" if feedback else f"{prompt}\n"

    st.text(f"*************** Generating Test case **********************")

    memory_generate = ConversationBufferWindowMemory(k=10)
    conversation_generate = ConversationChain(
        llm=llm_generator,
        memory=memory_generate
    )

    if feedback:
        worker_input = (f"{feedback}\n{FEEDBACK_PROMPT_WORKER}")
        st.text("************ Rewriting test cases as per feedback provided **************")
    else:
        worker_input = _format_prompt_worker(
            prompt,
            context_requirement=context,
            **unpack
        )

    # print(worker_input)

    worker_response = conversation_generate.invoke(worker_input)
    # pprint(worker_response)
    thoughts = extract_xml(worker_response['response'], "thoughts")
    test_cases = extract_xml(worker_response['response'], "test_cases")
    st.text(f"====== Thought ======\n{thoughts}\n")
    st.text(f"====== Test cases====\n{test_cases}\n")
    memory_generate.save_context({"thoughts": feedback}, {"test_cases": test_cases})

    return test_cases


def evaluate_test_case(context: str, prompt: str, test_cases: str, feedback: str = "") -> tuple[str, str]:
    """Evaluate if a solution meets requirements."""

    memory_eval = ConversationBufferWindowMemory(k=10)
    conversation_eval = ConversationChain(
        llm=llm_eval,
        memory=memory_eval
    )
    if feedback:
        eval_input = (f"{test_cases}\n{FEEDBACK_PROMPT_EVAL}")
        st.text("************ Evaluating test cases Again **************")

    else:
        full_prompt = f"{prompt}\n"
        st.text("************** Evaluating Test Case ****************")
        eval_input = _format_prompt_worker(
            full_prompt,
            Understanding=context,
            test_cases=test_cases,
            **unpack
        )

    eval_response = conversation_eval.invoke(eval_input)
    evaluation = extract_xml(eval_response['response'], "evaluation")
    feedback = extract_xml(eval_response['response'], "feedback")
    # pprint(worker_response)

    st.text(f"\n=== Eval RESULT ===\n{evaluation}\n{feedback}")
    memory_eval.save_context({"test cases": test_cases}, {"feedback": feedback})
    return evaluation, feedback
