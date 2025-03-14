import re
import os
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from prompts_helper import *
from helper_vectordb import *
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""


# retrieving the relevant documents from vector store
def retrieve_documents(query_text):
    """Fetching relevant document from vector store """

    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

    retriever = vectorstore.as_retriever()
    retrieve_doc = retriever.invoke(query_text)

    return retrieve_doc


def llm_call_orches(prompt: str, model="llama3-70b-8192") -> str:
    """
    Calls the model with the given prompt and returns the response.

    Args:
        prompt (str): The user prompt to send to the model.
        model (str, optional): The model to use for the call. Defaults to "llama3-70b-8192".

    Returns:
        str: The response from the language model.
    """

    # messages = [{"role": "user", "content": prompt}]
    memory = ConversationBufferWindowMemory(k=10)

    llm = ChatGroq(
        model_name = model,
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory
    )
    response = conversation.invoke(prompt)
    memory.save_context({"analysis": prompt}, {"response": str(response['response'])})
    return response

class Orchestrator:
    """Break down tasks and run them in parallel using worker LLMs."""

    def __init__(self, orchestrator_prompt: str):
        self.orchestrator_prompt = orchestrator_prompt

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required prompt variable: {e}")

    def process_llm(self, requirement, count):
        """Orchestrate tasks using the LLM based on the given requirement.

        Args:
            requirement (str): The requirement to process.

        Returns:
            str: Output from the orchestrator.
        """
        unpack = {}

        # retrieving and cleansing the document
        raw_documents = retrieve_documents(requirement)
        #documents = clean_text(raw_documents)

        if count > 0:
            self.orchestrator_prompt = f"{ORCHESTRATOR_PROMPT_MEMORY}"
            #print("************ Understanding Requirement Again **************")

        orchestrator_input = self._format_prompt(
            self.orchestrator_prompt,
            requirement=requirement,
            documents=raw_documents,
            **unpack
        )
        orchestrator_response = llm_call_orches(orchestrator_input)

        analysis = extract_xml(orchestrator_response['response'], "analysis")
        # test_scenarios = extract_xml(orchestrator_response['response'], "tests")

        #print("\n=== ORCHESTRATOR OUTPUT ===")
        # pprint(orchestrator_response)
        #print(f"\nANALYSIS:\n{analysis}")
        # print(f"\nTEST SCENARIOS:\n{test_scenarios}")

        return analysis
        # return {"Analysis": analysis, "Test Scenarios": test_scenarios}


orchestrator = Orchestrator(
    orchestrator_prompt=ORCHESTRATOR_PROMPT
)