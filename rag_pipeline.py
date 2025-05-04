import os
import git
import chromadb
import warnings

# Loading embeddings and vector store
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import GitLoader

# Querying with retriever
from openai import OpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from genconfig import repository, ai_service, clone_repo, template, collection_name, generate_image
from genconfig import openai_model, ollama_model, openai_image_model, ollama_embedding_model, openai_embedding_model
from genutils import get_local_path, get_vector_store_path, get_repository_path
from genutils import set_openai_api_key, format_docs, filter_repository_files, check_response_for_image

# Remove unused warnings and chromadb tenant issues
warnings.filterwarnings("ignore")
chromadb.api.client.SharedSystemClient.clear_system_cache()


class RagPipeline:  

    def __init__(self, uirepository=None):
        """
        Initializes the RAG pipeline.
        """
        if uirepository: 
            self.repository = uirepository
        else: 
            self.repository = repository
        print(f"Repository: {self.repository}")
        print(f"ai_service: {ai_service}")

        #Setup local and repo path
        self.local_path = get_local_path()
        self.vstore_path = get_vector_store_path()
        self.repo_path = get_repository_path(uirepository=uirepository)
        self.openai_api_key = set_openai_api_key()

        #Setup docs, vector store and retreiver
        self.vectorstore = None
        self.rag_retriever = None
        self.docs = None

        # Setup the retriever and vector store
        self.setup_rag_pipeline()

    def clone_repo(self):
        """
        Clones a Git repository to a local directory.
        """
        try:
            print("Cloning repository...")
            if os.path.exists(self.local_path):
                if not os.path.exists(self.repo_path):
                    git.Repo.clone_from(self.repository, self.repo_path)
            return self.repo_path
        except git.GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return None

    def load_git_documents(self):
        """
        Loads documents from a specified Git repository.
        Returns:
            A list of loaded documents or chunks.
        """
        try:
            print("Loading documents or chunks...")
            if clone_repo:
                try:
                    loader = GitLoader(repo_path=self.repo_path, branch="main", file_filter=filter_repository_files)
                    documents = loader.load_and_split()
                except Exception as e:
                    print(f"Error loading documents: {e}") 
                    loader = GitLoader(repo_path=self.repo_path, branch="master", file_filter=filter_repository_files)
                    documents = loader.load_and_split()
            else:
                try: 
                    loader = GitLoader(repo_path=self.repo_path, clone_url=self.repository, branch="main", file_filter=filter_repository_files)
                    documents = loader.load_and_split()
                except Exception as e:
                    print(f"Error loading documents: {e}") 
                    loader = GitLoader(repo_path=self.repo_path, clone_url=self.repository, branch="master", file_filter=filter_repository_files)
                    documents = loader.load_and_split()
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def setup_rag_pipeline(self):
        """
        Sets up the RAG pipeline using ChromaDB as the retriever.
        """
        try:
            print("Setting up RAG pipeline...")
            # Create embeddings, vectorstore and retriever
            embeddings = OllamaEmbeddings(model=ollama_embedding_model)
            if ai_service == "openai": 
                embeddings = OpenAIEmbeddings(model=openai_embedding_model)
            persistent_client = chromadb.PersistentClient(path=self.vstore_path)
            collection = persistent_client.get_or_create_collection(collection_name)
            self.vectorstore = Chroma(client=persistent_client,
                                      collection_name=collection_name, 
                                      embedding_function=embeddings, 
                                      create_collection_if_not_exists=True)
            print(f"Total Documents in vector store: {collection.count()}")

            if collection.count() <=0:
                self.docs = self.load_git_documents()
                if self.docs: 
                    print("Adding documents to store...")
                    docids = ["doc" + str(i+1) for i in range(len(self.docs))]
                    self.vectorstore.add_documents(documents=self.docs, ids=docids)

            # Set up the retriever
            self.rag_retriever = self.vectorstore.as_retriever()
            return self.rag_retriever
        except Exception as e:
            print(f"Error setting up RAG pipeline: {e}")
            return None

    def check_image_response(self, query, response):
        """
        Checks if the response can generate an image.
        """
        try:
            print("Checking image response...")
            image_url = None
            if check_response_for_image(response):
                nquery = f"""If the response can be represented by a meaningful image for architecture or process flow, 
                             create an image for the following response ```{response}``` representing architecture or process flow. 
                             Don't assume and if you can't create any relevant image, don't create."""
                client = OpenAI()
                response = client.images.generate(model=openai_image_model, prompt=nquery, size="1024x1024")
                if response and response.data and len(response.data) > 0:
                    image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Error checking image response: {e}")
            return None

    def ask_ai(self, query):
        """
        Sends a prompt to OpenAI and returns the response.
        """
        try:
            print(f"Initating response generation for {query}...")
            if self.rag_retriever is None:
                print("RAG retriever not set up.")
                return None

            # Use RetrievalQA chain
            if ai_service == "openai":
                llm = init_chat_model(openai_model, model_provider=ai_service, temperature=1)
            else:
                llm = OllamaLLM(model=ollama_model, temperature=0)
            prompt = ChatPromptTemplate.from_template(template)
            retrieval_chain = (
                {
                    "context": self.rag_retriever | format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
                | StrOutputParser()
            )

            # Get the response
            iresponse = None
            tresponse = retrieval_chain.invoke(query)
            # If generate image is true, check if the response can generate an image
            if generate_image and ai_service == "openai" and tresponse and len(tresponse) > 0:
                iresponse = self.check_image_response(query, tresponse)
            response = [tresponse, iresponse]
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return None


# Local Execution Loop
if __name__ == "__main__":
    print("RagPipeline for Public Repository Queries")
    rpipeline = RagPipeline()
    query = "Review the code, explain purpose and architecture of Flask framework."
    response = rpipeline.ask_ai(query)
    print(f"{response}")
    print("RAG pipeline set up successfully.")