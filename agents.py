from crewai import Agent

# Agent for vectorization and storage
data_vectorizer = Agent(
    role='Data Vectorizer',
    goal='Vectorize provided content and store it in a vector database using OpenAI embeddings.',
    verbose=True,
    memory=True,
    tools=[],
    allow_delegation=False
)

# Agent for retriever with refinement
retriever = Agent(
    role='Retriever Designer',
    goal='Design a retriever to search vectorized data, refine the top documents, and return combined relevant knowledge.',
    verbose=True,
    memory=True,
    tools=[],
    allow_delegation=False
)

# Agent for chatbot with enhanced correction
chatbot_agent = Agent(
    role='Chatbot Designer',
    goal="Implement a chatbot that dynamically adjusts its responses based on the user's query intent, combining and refining multiple knowledge sources if needed.",
    verbose=True,
    memory=True,
    tools=[],
    allow_delegation=False
)
