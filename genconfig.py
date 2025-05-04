# Repository for loacal execution
# repository = "https://github.com/smallest-inc/smallest-python-sdk.git" # - 293
# repository = "https://github.com/simular-ai/Agent-S.git" # - 153
repository = "https://github.com/pallets/flask.git" # - 460

# Repositories for steamlit execution
repositories = [None, 
                "https://github.com/pallets/flask.git",
                "https://github.com/smallest-inc/smallest-python-sdk.git",
                "https://github.com/simular-ai/Agent-S.git"]
# local paths and configurations
temp_folder = "temp"
clone_repo = False
generate_image = False

# Prompt Template
template="""You are a code reviewer and you are supposed to look at all python code files along with Readme. Use the following pieces of retrieved context from repository files to answer the question. Represent process flow diagrams or architecture diagrams as markdown. Keep the answer concise. If you don't know the answer, just say that you don't know.\nContext: {context}\nQuestion: {question}  \nAnswer:"""

# Set LLM and Embedding 
ai_service = "openai" #  openai / ollama

# open ai specific config
openai_model = "o4-mini" # "gpt-4o-mini", "gpt-4o"
openai_image_model = "dall-e-3" # "gpt-image-1"
openai_embedding_model = "text-embedding-3-small"
temperature = 1

# ollama specific config
ollama_model = "deepseek-r1:1.5b" # "llama3.2:1b"
ollama_embedding_model = "nomic-embed-text"

# Vector store config
vstore_path = "vstore"
collection_name = "repository_files"