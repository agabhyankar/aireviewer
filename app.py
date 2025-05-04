import streamlit as st

from genconfig import repositories
from genutils import reset_local_path
from rag_pipeline import RagPipeline

# To fix the chromadb error and later replace chromadb
import chromadb
chromadb.api.client.SharedSystemClient.clear_system_cache()


# Initialize the session state
print("Initializing session state and UI components...")
if "reviewer" not in st.session_state:
    print("Initializing session reviewer...")
    st.session_state.reviewer = None
if "messages" not in st.session_state:
    print("Initializing session messages...")
    st.session_state.messages = []
if "repository" not in st.session_state:
    print("Initializing session repository...")    
    st.session_state.repository = None


def show_progress_bar(progress, text):
    """
    Show a progress bar in the Streamlit app.
    """
    progress_bar = st.progress(progress, text=text)
    return progress_bar


def initialize_rag_pipeline(reset=False):
    """
    Initialize the RAG pipeline.
    """
    ptext = "(Re)Initializing RAG pipeline..."
    ptext1 = "(Re)Initializing RAG pipeline in process..."
    ptext2 = "RAG pipeline initialized successfully!"
    progress_bar = show_progress_bar(0, text=ptext)
    progress_bar.progress(10, text=ptext1)
    try:
        if reset:
            reset_local_path()
            progress_bar.progress(30, text=ptext1)
            st.session_state.messages = []
            st.session_state.reviewer = None
        rpipeline = RagPipeline(uirepository=st.session_state.repository)
        progress_bar.progress(80, text=ptext1)
        st.session_state.reviewer = rpipeline
        if reset:
            st.sidebar.success("RAG pipeline reset successfully!")
        else:
            st.sidebar.success("RAG pipeline initialized successfully!")
        progress_bar.progress(90, text="(Re)Initializing RAG pipeline in process...")
    except Exception as e:
        st.sidebar.error(f"Error initializing RAG pipeline: {e}")
    progress_bar.progress(100, text=ptext2)
    progress_bar.empty()


# Set basic UI components
st.set_page_config(layout="wide")
st.title("Repository Code Reviewer")
st.divider()


# Set the UI Configuration controls
with st.sidebar:
    st.sidebar.title("Configure")
    st.sidebar.divider()

    # Choose the repository
    repository = st.selectbox(
        "Select a repository",
        repositories,
    )
    if repository:
        if repository != st.session_state.repository:
            st.sidebar.write(repository)
            st.session_state.repository = repository
            st.sidebar.success(f"Repository: {repository}")
            initialize_rag_pipeline(reset=True)
        else:
            initialize_rag_pipeline()
    st.sidebar.divider()

    # Initialize the RAG pipeline
    rag_pipeline = st.sidebar.button("Initialize RAG Pipeline")
    if rag_pipeline: 
        initialize_rag_pipeline()
    st.sidebar.divider()

    # Reset the RAG pipeline
    reset_rag_pipeline = st.sidebar.button("Reset RAG Pipeline")
    if reset_rag_pipeline: 
        initialize_rag_pipeline(reset=True)
    st.sidebar.divider()

    # Initialize the RAG pipeline
    reset_session = st.sidebar.button("Reset Message History")
    if reset_session: 
        st.session_state.messages = []
    st.sidebar.divider()


# Write earlier messages
if "messages" in st.session_state and len(st.session_state.messages) > 0:
    print("Writing earlier messages...")
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            if isinstance(message["content"], list):
                for res in message["content"]:
                    if res:
                        if res is not None and res.startswith("http"):
                            st.chat_message("assistant").image(res, width=500, caption="Generated Image")
                        else:            
                            st.chat_message("assistant").markdown(res)


# Initiate chat control
prompt = st.chat_input("Enter your question here...")
if prompt:
    ptext = "Generating response..."
    progress_bar = show_progress_bar(0, text=ptext)
    progress_bar.progress(10, text=ptext)

    # Set the new message
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    progress_bar.progress(30, text=ptext)
    if st.session_state.repository is None or st.session_state.reviewer is None:
        st.error("Choose the repository and initialize the RAG pipeline first!")
    else:
        reviewer = st.session_state.reviewer
        response = reviewer.ask_ai(prompt)
        progress_bar.progress(80, text=ptext)        
        st.session_state.messages.append({"role": "assistant", "content": response})
        if isinstance(response, list):
            for res in response:
                if res:
                    if res.startswith("http"):
                        st.chat_message("assistant").image(res, width=500, caption="Generated Image")
                    else:            
                        st.chat_message("assistant").markdown(res)
        else:
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    ptext = "Generated response..."
    progress_bar.progress(100, text=ptext)
    progress_bar.empty()
