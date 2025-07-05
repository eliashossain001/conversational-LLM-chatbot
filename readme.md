# Chat-With-Web-using-CrewAI

## Overview

CrewAI is a sophisticated workflow built for processing, retrieving, and generating dynamic responses from a vast dataset. The system involves several agents working together to vectorize, retrieve, and create chatbot responses using OpenAI's GPT models and other integrated tools like Google Custom Search for external knowledge.

The CrewAI workflow is divided into several components, each focusing on a specific task, such as vectorization, retriever design, and chatbot implementation. The system is flexible and can be extended to accommodate more tasks and features as needed.

---

## Workflow

1. **Vectorization**: The data is vectorized and stored in a database using OpenAI embeddings.
2. **Retriever Design**: A retriever is designed to search the vectorized data and refine the search results.
3. **Chatbot Implementation**: A chatbot is created that dynamically adjusts its responses based on the query intent.

The system ensures that input is sanitized, validated, and signed for security, using cryptographic signatures for query verification.

---

## Components

### 1. `agents.py`
This file defines the different agents used in the workflow:

- **Data Vectorizer Agent**: Responsible for vectorizing content and storing it in a vector database.
- **Retriever Designer Agent**: Designs a retriever to search and refine vectorized data.
- **Chatbot Agent**: Implements a chatbot that dynamically adjusts its responses based on user queries.

### 2. `crew.py`
This file defines the main workflow of the CrewAI system, using the agents to perform tasks like vectorization, retriever design, and chatbot response generation. The flow involves:

- Generating a signed query.
- Processing and sanitizing the input.
- Passing the query through the steps of vectorization, retriever design, and chatbot implementation.

### 3. `prompt_inject.py`
This file contains utilities for handling and verifying signed prompts:

- **Generate Signed Prompt**: Creates a cryptographic signature for the query to ensure its authenticity.
- **Verify Signed Prompt**: Verifies the signature of the prompt.
- **Sanitize and Validate Input**: Ensures input is free from harmful patterns and is within allowed length.

### 4. `tasks.py`
This file defines the tasks that the system performs:

- **Vectorize Data**: Converts data into a vectorized format and stores it in a database.
- **Design Retriever**: Creates a retriever using the vector database.
- **Implement Chatbot**: Implements a chatbot using a retriever for dynamic responses.
- **Format Responses**: Formats the response from the chatbot based on the query type (list or paragraph).

### 5. `tools.py`
This file defines the tools for creating a vector database and setting up the retriever and chatbot:

- **Create Vector Database**: Uses OpenAI embeddings to create a vector database from a JSON file.
- **Setup Retriever**: Configures a retriever to search the vectorized database.
- **Build Chatbot**: Builds a chatbot using OpenAI's GPT model and integrates web search for external knowledge.

---

## Setup

### Prerequisites

- Python 3.x
- OpenAI API Key
- Google API Key (for web search)
- Google Custom Search Engine ID

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/crewai-workflow.git
   cd crewai-workflow
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file in the root directory.
   - Add the following keys:
     ```env
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     GOOGLE_SEARCH_ENGINE_ID=your_google_cse_id
     SECRET_KEY=your_secret_key
     ```

4. Run the system:
   ```bash
   streamlit run app.py
   ```

---

## Usage

Once the setup is complete, you can use the system to process queries. The `crew_workflow` function in `crew.py` takes a user query and processes it through the vectorization, retriever design, and chatbot implementation steps.

Example:
```python
from crew import crew_workflow

query = "What is the significance of AI in modern education?"
result = crew_workflow(query)
print(result)
```

This will return a structured response with the chatbot's answer and relevant sources.

---

## Error Handling

- **Input Errors**: If the input contains harmful patterns or exceeds the length limit, a `SanitizationError` is raised.
- **Vectorization Errors**: If the vectorization step fails, an error message is returned.
- **Retriever Errors**: If the retriever design step fails, an error message is returned.
- **Chatbot Errors**: If the chatbot implementation fails, an error message is returned.

---

## Contributing

We welcome contributions to enhance the functionality of CrewAI! Feel free to fork the repository, make improvements, and submit pull requests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- OpenAI for providing powerful language models.
- Google for the Custom Search API to retrieve external knowledge.

---





