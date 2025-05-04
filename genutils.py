import os
import shutil

from genconfig import temp_folder, vstore_path, repository


def get_local_path():
    """
    Get the local path for storing the vector store and repository.
    """
    local_path = os.path.join(os.getcwd(), temp_folder)
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    return local_path


def get_vector_store_path():
    """
    Get the path to the vector store.
    """
    local_path = get_local_path()
    vector_store_path = os.path.join(local_path, vstore_path)
    return vector_store_path


def get_repository_path(uirepository=None):
    """
    Get the path to the repository.
    """
    if uirepository: 
        repo_path = uirepository
    else: 
        repo_path = repository
    local_path = get_local_path()
    repository_path = os.path.join(local_path, os.path.basename(repo_path))
    return repository_path


def format_docs(docs):
    """Format the documents for display."""
    return "\n\n".join(doc.page_content for doc in docs)


def filter_repository_files(file_path: str) -> bool:
    """Filter files in the repository based on their extensions or name."""
    if file_path.endswith(".py") or file_path.endswith(".md") or file_path.lower().find("README") >= 0:
        return True
    return False


def set_openai_api_key():
    """
    Get the OpenAI API key from environment variables.
    """
    from dotenv import dotenv_values
    CONFIG = dotenv_values(".env")
    openai_api_key = CONFIG.get("OPENAI_KEY", "")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in environment variables.")
    else:
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key


def reset_local_path():
    """
    Reset the local path by deleting the existing one and creating a new one.
    """
    local_path = get_local_path()
    # Check if the local path exists
    if os.path.exists(local_path):
        # Delete the existing vector store
        shutil.rmtree(local_path)
    return


def check_response_for_image(text):
    """
    Check if the text is proper to generate an image.
    Other checks can be added here.
    """
    if text.lower().find("i don't know.") < 0: 
        return True
    return False