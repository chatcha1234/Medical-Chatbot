from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from pinecone import Pinecone
import os
import time

class PDFSearchTool(BaseTool):
    name: str = "Medical Search"
    description: str = (
        "Useful for searching and extracting information from the medical encyclopedia (PDFs). "
        "Input should be a search query in English."
    )
    
    def _run(self, query: str) -> str:
        if not os.getenv("PINECONE_API_KEY"):
            return "Error: PINECONE_API_KEY not found."
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = "medical-chatbot"

        # Check for index
        existing_indexes = [index.name for index in pc.list_indexes()]
        if index_name not in existing_indexes:
            return "The medical database is not initialized. Please run ingestion."

        vectorstore = LangchainPinecone.from_existing_index(index_name=index_name, embedding=embeddings)
        
        try:
            results = vectorstore.similarity_search(query, k=3)
            if not results:
                return "No specific information found. Suggest general medical advice or see a doctor."
            
            formatted_results = []
            for doc in results:
                source = os.path.basename(doc.metadata.get('source', 'Unknown'))
                page = doc.metadata.get('page', 'N/A')
                content = doc.page_content.replace('\n', ' ')
                formatted_results.append(f"[SOURCE: {source}, PAGE: {page}]\nCONTENT: {content}")
            
            return "\n\n---\n\n".join(formatted_results)
        except Exception as e:
            return f"Error during search: {str(e)}"

class MedicalTools:
    def __init__(self):
        self.medical_search = PDFSearchTool()
