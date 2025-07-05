import os
import json
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from googleapiclient.discovery import build
import hashlib

def compute_file_hash(file_path):
    """Compute a hash for the contents of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_vector_database(json_file_path):
    """Create a vector database using ChromaDB with `text-embedding-3-small`."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set it in your environment variables.")

    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)
    persist_directory = "db"

    # Check if database already exists and is up to date
    if os.path.exists(persist_directory) and os.path.exists(json_file_path):
        new_hash = compute_file_hash(json_file_path)
        hash_file = os.path.join(persist_directory, "data_hash.txt")
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                existing_hash = f.read()
            if existing_hash == new_hash:
                print("No changes detected in data. Using existing embeddings.")
                return Chroma(persist_directory=persist_directory, embedding_function=openai_embeddings)

    # Load and process the JSON data
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = [
        Document(page_content=item["content"], metadata={"title": item["title"], "url": item["url"]})
        for item in data
    ]
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=40)
    docs = text_splitter.split_documents(documents)

    # Create the vector database - persistence is automatic in newer versions
    vectordb = Chroma.from_documents(
        documents=docs, 
        embedding=openai_embeddings, 
        persist_directory=persist_directory
    )
    
    # Note: vectordb.persist() is no longer needed in newer versions
    # The database automatically persists when persist_directory is specified

    # Save the hash for future comparison
    new_hash = compute_file_hash(json_file_path)
    with open(os.path.join(persist_directory, "data_hash.txt"), 'w') as f:
        f.write(new_hash)

    return vectordb

def setup_retriever(vector_database):
    """Setup a retriever using the vector database."""
    return vector_database.as_retriever(search_kwargs={"k": 3})

def build_chatbot(retriever):
    """Build a chatbot using OpenAI's GPT model."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set it in your environment variables.")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    target_website = os.getenv("TARGET_WEBSITE")

    def search_web(query, max_results=1):
        """Perform web search to retrieve external knowledge."""
        if not google_api_key or not google_cse_id:
            return []
        
        try:
            service = build("customsearch", "v1", developerKey=google_api_key)
            results = service.cse().list(q=query, cx=google_cse_id, siteSearch=target_website, num=max_results).execute()
            return results.get("items", [])
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def refine_documents(documents, max_tokens=1500):
        """Decompose, filter, and recompose documents into refined knowledge."""
        refined_content = []
        current_token_count = 0

        for doc in documents:
            # Decompose into smaller chunks
            chunks = doc.page_content.split("\n")
            # Filter relevant chunks
            filtered_chunks = [chunk for chunk in chunks if len(chunk.strip()) > 20]

            # Add chunks until max_tokens is reached
            for chunk in filtered_chunks:
                token_count = len(chunk.split())
                if current_token_count + token_count > max_tokens:
                    break
                refined_content.append(chunk)
                current_token_count += token_count

        return "\n".join(refined_content)

    llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key, max_tokens=500)  # Limit output tokens
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    def answer_with_sources(query):
        dynamic_prompt = (
            "Respond dynamically based on the query intent. "
            "Use a paragraph for general information and a list for enumerations. "
            "Maintain a professional tone.\n\nQuery:"
        )

        # Step 1: Retrieve the top k documents
        documents = retriever.get_relevant_documents(query)

        # Step 2: Refine documents
        refined_knowledge = refine_documents(documents, max_tokens=1500)

        # Step 3: Fallback to web search if needed
        if not refined_knowledge.strip():
            web_results = search_web(query, max_results=1)
            if web_results:
                refined_knowledge = "\n".join(
                    f"{item['title']}: {item['link']}" for item in web_results
                )

        # Step 4: Enforce strict token limit for input
        total_input = f"{refined_knowledge}\n\n{dynamic_prompt}\n\n{query}"
        if len(total_input.split()) > 4000:  # Strict input token cap
            total_input = " ".join(total_input.split()[:4000])

        # Step 5: Generate response
        response = qa_chain.run(total_input)

        source_url = documents[0].metadata.get("url", "No URL provided") if documents else "No URL provided"

        return {
            "result": response,
            "sources": [source_url]  # Return only the top source URL
        }

    return answer_with_sources