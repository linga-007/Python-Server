import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
import tempfile
import time

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

prompt = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}
""")

def create_pdf_from_string(data):
    """
    Creates a temporary PDF file from a given string.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_canvas = canvas.Canvas(tmp_file.name)
        pdf_canvas.drawString(100, 750, data)
        pdf_canvas.save()
        return tmp_file.name

def vector_embedding_from_temp_file(pdf_path):
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectors = FAISS.from_documents(final_documents, embeddings)

    return vectors, final_documents

def get_response_from_embedding(vectors, question):
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    response = retrieval_chain.invoke({'input': question})
    response_time = time.process_time() - start

    return response, response_time

def process(content , question):
    pdf_path = create_pdf_from_string(content)
    vectors, documents = vector_embedding_from_temp_file(pdf_path)
    response, response_time = get_response_from_embedding(vectors, question)
    return [response , response_time]
