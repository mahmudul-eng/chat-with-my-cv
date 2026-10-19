import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

st.set_page_config(page_title="Chat with Mahmudul's CV", page_icon="💬")

CV_PATH = "cv.pdf"
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b") 

EXAMPLES = [
    "What projects has he built?",
    "What is his educational background?",
    "Which programming languages and tools does he know?",
]

SYSTEM_PROMPT = """You answer questions about Mahmudul's background using only the CV context below.
If the answer is not in the context, say you don't have that information and suggest contacting him.
Keep answers short and friendly. Refer to him in the third person.

CV context:
{context}

Conversation so far:
{history}
"""


def get_api_key():
    # Streamlit Cloud: App settings -> Secrets. Local: environment variable or .streamlit/secrets.toml
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


# ---------- Load and index the CV once (cached across reruns) ----------
@st.cache_resource(show_spinner="Loading the CV...")
def load_retriever():
    docs = PyPDFLoader(CV_PATH).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, embeddings)
    return db.as_retriever(search_kwargs={"k": 4})


@st.cache_resource
def load_llm(api_key):
    return ChatGroq(model=MODEL_NAME, temperature=0.2, api_key=api_key)


def answer_question(question, history, retriever, llm):
    last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    found = retriever.invoke(f"{last_user} {question}".strip())

    context = "\n\n".join(d.page_content for d in found)
    hist = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history[-8:])
    prompt = SYSTEM_PROMPT.format(context=context, history=hist) + f"\nUser question: {question}\nAnswer:"

    try:
        reply = llm.invoke(prompt).content
    except Exception as e:
        print("ERROR:", e)  # visible in the app logs
        if "429" in str(e):
            return "The assistant is busy right now. Please try again in a minute."
        return "Sorry, something went wrong. Please try again."

    pages = sorted({d.metadata.get("page", 0) + 1 for d in found})
    return f"{reply}\n\n_Source: CV page {', '.join(map(str, pages))}_"


# ---------- UI ----------
st.title("Chat with Mahmudul's CV")
st.caption("Ask about my skills, projects, education, or experience.")

api_key = get_api_key()
if not api_key:
    st.error("GROQ_API_KEY is missing. Add it in the app's Secrets settings.")
    st.stop()

retriever = load_retriever()
llm = load_llm(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

user_input = st.chat_input("Ask something about the CV...")
question = user_input or st.session_state.pending
st.session_state.pending = None
if question:
    st.session_state.messages.append({"role": "user", "content": question})

if not st.session_state.messages:
    st.write("Try one of these:")
    for q in EXAMPLES:
        if st.button(q):
            st.session_state.pending = q
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if question:
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = answer_question(question, st.session_state.messages[:-1], retriever, llm)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
