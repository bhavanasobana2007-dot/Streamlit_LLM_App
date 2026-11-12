
import os
import time
import streamlit as st

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

from pdf_qa import (
    create_vector_store,
    get_answer,
    save_result
)


# Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "dataset")
UPLOAD_PATH = os.path.join(DATASET_PATH, "uploaded_files")
ASSETS_PATH = os.path.join(BASE_DIR, "assets")

SAMPLE_PATH = os.path.join(DATASET_PATH, "sample.pdf")
LOGO_PATH = os.path.join(ASSETS_PATH, "logo.png")

os.makedirs(UPLOAD_PATH, exist_ok=True)


# Page configuration
st.set_page_config(
    page_title="Education AI Assistant",
    page_icon="🎓",
    layout="wide"
)


# Load embedding model
@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# Load Ollama model
@st.cache_resource
def load_llm():

    return OllamaLLM(
        model="llama3.2:3b"
    )


# Sidebar
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=130)

st.sidebar.title("🎓 Education AI Assistant")

st.sidebar.write(
    "Ask questions from your PDF documents."
)

st.sidebar.divider()


# Main title
st.title("📚 AI PDF Question Answering System")

st.write(
    "Upload your PDF and ask questions. "
    "Get answers using Artificial Intelligence."
)


# HOME ACTIVITY 1
# Multiple PDF Upload

uploaded_files = st.file_uploader(
    "Upload PDF Documents",
    type=["pdf"],
    accept_multiple_files=True
)


# Save uploaded PDFs
if uploaded_files:

    for uploaded_file in uploaded_files:

        pdf_bytes = uploaded_file.getvalue()

        if not pdf_bytes.startswith(b"%PDF"):
            st.error(
                f"{uploaded_file.name} is not a valid PDF."
            )
            continue

        safe_name = os.path.basename(uploaded_file.name)

        save_path = os.path.join(
            UPLOAD_PATH,
            safe_name
        )

        with open(save_path, "wb") as file:
            file.write(pdf_bytes)


# Get available PDFs
pdf_names = []

if os.path.isfile(SAMPLE_PATH):
    pdf_names.append("sample.pdf")


if os.path.isdir(UPLOAD_PATH):

    for filename in os.listdir(UPLOAD_PATH):

        if filename.lower().endswith(".pdf"):
            pdf_names.append(filename)


pdf_names = sorted(set(pdf_names))


# Check PDF availability
if not pdf_names:

    st.warning("Please upload a PDF document.")

    st.stop()


# Select PDF
selected_pdf = st.selectbox(
    "Select PDF Document",
    pdf_names,
    index=0
)


# HOME ACTIVITY 2
# Display PDF details

if selected_pdf is None:

    st.warning("Please select a PDF document.")

    st.stop()


if selected_pdf == "sample.pdf":

    selected_path = SAMPLE_PATH

else:

    selected_path = os.path.join(
        UPLOAD_PATH,
        selected_pdf
    )


if not os.path.isfile(selected_path):

    st.error("Selected PDF file not found.")

    st.stop()


with open(selected_path, "rb") as file:

    pdf_bytes = file.read()


# Validate PDF
if not pdf_bytes.startswith(b"%PDF"):

    st.error("Invalid PDF file.")

    st.stop()


# Load AI models and PDF
try:

    with st.spinner("Loading PDF and AI models..."):

        embeddings = load_embeddings()

        llm = load_llm()

        vector_store, page_count, chunk_count, file_hash = (
            create_vector_store(
                pdf_bytes,
                embeddings
            )
        )

    st.success("PDF loaded successfully!")

except Exception as error:

    st.error(f"Error loading PDF: {error}")

    st.stop()


# Display document information
st.subheader("📄 Document Information")

col1, col2 = st.columns(2)

col1.metric(
    "Total PDF Pages",
    page_count
)

col2.metric(
    "Total Text Chunks",
    chunk_count
)

st.write(
    "**Selected PDF:**",
    selected_pdf
)


# Chat history
if "chat_history" not in st.session_state:

    st.session_state.chat_history = {}


if file_hash not in st.session_state.chat_history:

    st.session_state.chat_history[file_hash] = []


history = st.session_state.chat_history[file_hash]


# HOME ACTIVITY 3
# Clear chat history

if st.sidebar.button("🗑️ Clear Chat History"):

    st.session_state.chat_history[file_hash] = []

    st.rerun()


st.sidebar.success(
    f"Selected PDF: {selected_pdf}"
)

st.sidebar.caption(
    "Powered by Streamlit, LangChain and Ollama"
)


# HOME ACTIVITY 4
# Conversation history

st.divider()

st.subheader("💬 Ask Your Question")


question = st.chat_input(
    "Type your question here..."
)


if question:

    history.append({
        "role": "user",
        "content": question
    })

    start_time = time.time()

    try:

        with st.spinner("Generating AI Answer..."):

            answer, retrieved_docs = get_answer(
                question,
                vector_store,
                llm
            )

        response_time = round(
            time.time() - start_time,
            2
        )

        sources = []

        for doc in retrieved_docs:

            sources.append({
                "page": doc.metadata.get("page", 0) + 1,
                "content": doc.page_content
            })


        history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "response_time": response_time
        })


        # Save question and answer
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        save_result(
            "queries.csv",
            {
                "timestamp": timestamp,
                "document": selected_pdf,
                "question": question
            }
        )

        save_result(
            "answers.csv",
            {
                "timestamp": timestamp,
                "document": selected_pdf,
                "question": question,
                "answer": answer,
                "response_time_seconds": response_time
            }
        )


    except Exception as error:

        history.append({
            "role": "assistant",
            "content": f"Error: {error}",
            "sources": [],
            "response_time": 0
        })


# Display chat history
st.subheader("Conversation History")


for message in history:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant":

            st.caption(
                "Response Time: "
                + str(message.get("response_time", 0))
                + " seconds"
            )


            # HOME ACTIVITY 5
            # Retrieved PDF chunks

            sources = message.get("sources", [])

            if sources:

                with st.expander(
                    "📖 View Retrieved PDF Sections"
                ):

                    for index, source in enumerate(
                        sources,
                        start=1
                    ):

                        st.markdown(
                            f"**Chunk {index} - "
                            f"Page {source['page']}**"
                        )

                        st.write(
                            source["content"]
                        )

                        st.divider()


# Footer
st.divider()

st.caption(
    "Education AI Assistant | Week 14 Home Activity"
)
