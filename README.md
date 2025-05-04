# AI Code Reviewer (Chatbot)

## Objective

The goal is to design and implement a chatbot that analyses a given code
repository and provides relevant responses to user queries based on the
repository's content. The chatbot should be capable of fetching information from
the repository, understanding code structures, and assisting users in debugging
or comprehending the project.

## Requirements
- Basic UI/UX
  - Basic browser-based UI for a user to interact with the chatbot
- Repository Integration
  - The chatbot should be able to connect to a public repository e.g. GitHub
- NLP
  - Process user queries and map it to relevant repository content
- Semantic Review
  - Utilise LLMs to review and understand code
- Response Generation
  - Generate an appropriate response
- Other
  - Use of embeddings to enhance semantic search
  - Generate images based on generated response
  - Future enhancements and suggestions

## Technical Considerations
- Programming Language:
  - Python and relevant extensions defined in requirements.txt
- Frameworks, Store & API’s:
  - Langchain, OpenAI, Ollama, Streamlit, ChromaDB etc,

## Deliverables
- Documentation regarding implementation details
- Code or code repository

## Setup
- Pre-requisites
  - Ollama should be pre-installed if Ollama is used
  - LLMs required should be pulled using Ollama in case Ollama is used
  - OpenAI API Key should be set in the .env file
    - OPENAI_KEY = YOUR_OPEN_AI_KEY
- Download the repository
  - Setup virtual environment
  - Install requirements (pip install -r requirements.txt)
  - Update the required configuration in genconfig if required
  - Execute streamlit application

## Future Enhancements
- Choices
  - AI API's (for e.g. Ollama or OpenAI or any other)
  - LLMs (for e.g. gpt-3.5-turbo, gpt-4o)
  - Vector stores (for e.g. FAISS, pinecone)
- Support for rendering mermaid charts
- Generate images for flow and architecture diagrams
- Authentication & Authorization
- Perfomance Monitoring & Logging
- Docker and Containerization
