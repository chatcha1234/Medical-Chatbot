import os
import time
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    print("🚀 Starting data ingestion (Smart Mode)...")
    
    # Check API Keys
    if not os.getenv("PINECONE_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: API Keys missing.")
        return

    # Initialize Embeddings
    model_name = "models/gemini-embedding-001"
    embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
    
    # 🕵️ Detect Dimension
    print(f"🕵️ Detecting dimension for model: {model_name}...")
    try:
        sample_vector = embeddings.embed_query("test")
        dimension = len(sample_vector)
        print(f"✅ Detected Dimension: {dimension}")
    except Exception as e:
        print(f"❌ Error detecting dimension: {e}")
        return

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "medical-chatbot"

    # 🗑️ Delete if Exists (Force Rebuild to fix mismatch)
    existing_indexes = [index.name for index in pc.list_indexes()]
    if index_name in existing_indexes:
        print(f"⚠️ Index '{index_name}' exists. Checking compatibility...")
        try:
            desc = pc.describe_index(index_name)
            if desc.dimension != dimension:
                print(f"🗑️ Dimension mismatch ({desc.dimension} vs {dimension}). Deleting old index...")
                pc.delete_index(index_name)
                time.sleep(5) # Wait for deletion
            else:
                print("✅ Index dimension matches. Appending data...")
        except Exception as e:
            print(f"❌ Error checking index: {e}")
            # Try delete anyway if check fails
            try:
                pc.delete_index(index_name)
            except:
                pass

    # Create Index if needed
    existing_indexes = [index.name for index in pc.list_indexes()] # Re-check
    if index_name not in existing_indexes:
        print(f"📦 Creating index: {index_name} with dimension {dimension}...")
        try:
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return

    # Load Data
    data_path = os.path.join(os.getcwd(), "data")
    loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        print("⚠️ No documents found.")
        return

    print(f"📄 Found {len(documents)} pages. Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Total chunks to process: {len(chunks)}")

    # Initialize VectorStore
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

    # BATCH UPLOAD (Optimized for Paid Key)
    BATCH_SIZE = 100
    DELAY_SECONDS = 0.1
    
    print("🧠 Uploading to Pinecone in batches...")
    total_chunks = len(chunks)
    for i in range(0, total_chunks, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        print(f"   Using batch {i+1} to {min(i+BATCH_SIZE, total_chunks)} of {total_chunks}")
        
        try:
            vectorstore.add_documents(batch)
            time.sleep(DELAY_SECONDS)
        except Exception as e:
            print(f"   ⚠️ Error in batch {i}: {e}")
            print("   Waiting 60s cooldown...")
            time.sleep(60)
            try:
                vectorstore.add_documents(batch)
            except Exception as e2:
                print(f"   ❌ Batch failed after retry: {e2}")

    print("🎉 Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()
