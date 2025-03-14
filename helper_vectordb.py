import uuid
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
persist_directory = "chromadb_store"

def format_chunk(pdf_path):

    reader = PdfReader(pdf_path) # Create a PdfReader object

    pdf_text = ""  # Initialize a variable to store the text

    for page in reader.pages:  # Iterate through all pages and extract text
        pdf_text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=500,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )

    all_splits = text_splitter.create_documents([pdf_text])

    return all_splits

def vector_store(requirement_texts):

    unique_collection_name = f"collection_{uuid.uuid4()}"

    vectorstore = Chroma.from_documents(requirement_texts, collection_name=unique_collection_name,
                                        embedding=embeddings_model, persist_directory=persist_directory)

    return vectorstore




