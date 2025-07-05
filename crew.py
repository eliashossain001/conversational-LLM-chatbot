import os
from dotenv import load_dotenv
from tasks import vectorize_data, design_retriever, implement_chatbot, format_responses
from prompt_inject import process_input, generate_signed_prompt

# Load environment variables
load_dotenv()

JSON_FILE_PATH = r"PUT THE JSON PATH HERE"
SECRET_KEY = os.getenv("SECRET_KEY")  # Add your secret key to the .env file

def crew_workflow(query):
    try:
        # Generate a signed version of the query
        if SECRET_KEY:
            query = generate_signed_prompt(query, SECRET_KEY)

        # Process the input (sanitize, validate, check signed prompt)
        query = process_input(query, secret_key=SECRET_KEY)
    except ValueError as e:
        # Return a specific error message
        return {"error": str(e)}

    # Step 1: Vectorize provided data
    vectorization_result = vectorize_data({"json_file_path": JSON_FILE_PATH})
    if "error" in vectorization_result:
        return {"error": vectorization_result["error"]}

    # Step 2: Design retriever with refinement
    retriever_result = design_retriever({"vector_database": vectorization_result["database"]})
    if "error" in retriever_result:
        return {"error": retriever_result["error"]}

    # Step 3: Implement chatbot and answer the query
    chatbot_result = implement_chatbot({"retriever": retriever_result["retriever"]})
    if "error" in chatbot_result:
        return {"error": chatbot_result["error"]}

    # Get the chatbot function
    chatbot = chatbot_result["chatbot"]

    # Query the chatbot
    response = chatbot(query)
    query_type = "list" if "list" in query.lower() else "paragraph"
    formatted_response = format_responses(response.get("result", ""), query_type)
    sources = response.get("sources", [])

    return {
        "status": "success",
        "response": formatted_response,
        "sources": sources
    }
