# 💬 Chat with My CV

A RAG (Retrieval-Augmented Generation) chatbot that answers questions about my CV. Visitors can ask about my skills, projects, education, and experience, and the assistant answers using only the content of my CV.

**Live demo:** [chat-with-mahmudul.streamlit.app](https://chat-with-mahmudul.streamlit.app/)

## Features

- Answers grounded in the CV, with the source page shown under each answer
- Remembers earlier messages, so follow-up questions work
- Says so when the answer is not in the CV, instead of guessing
- Example question buttons to get started quickly
- Fast responses powered by Groq

## How it works

1. **Load:** the CV PDF is read with `PyPDFLoader`.
2. **Split:** the text is cut into small overlapping chunks.
3. **Embed:** each chunk is converted into a vector with `sentence-transformers/all-MiniLM-L6-v2`.
4. **Store:** the vectors are kept in a FAISS index in memory.
5. **Retrieve:** for each question, the 4 most relevant chunks are found.
6. **Generate:** the chunks, chat history, and question are sent to a Groq-hosted LLM, which writes the answer.

## Tech stack

| Part | Tool |
| --- | --- |
| UI | Streamlit |
| Orchestration | LangChain |
| LLM | Groq (Llama 3.3 70B by default) |
| Embeddings | Hugging Face sentence-transformers |
| Vector store | FAISS |
| PDF loading | pypdf |

## Project structure

```
chat-with-my-cv/
├── app_streamlit.py     # the Streamlit app
├── requirements.txt     # Python packages
├── cv.pdf               # the CV used as the knowledge base
└── README.md
```

## Run locally

1. Clone the repository and open the folder:

   ```bash
   git clone https://github.com/mahmudul-eng/chat-with-my-cv.git
   cd chat-with-my-cv
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS / Linux
   ```

3. Install the packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Get a free API key from [console.groq.com](https://console.groq.com) and save it in `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your_key_here"
   ```

5. Run the app:

   ```bash
   streamlit run app_streamlit.py
   ```

## Configuration

| Setting | Where | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | Streamlit secrets or environment variable | Your Groq API key (required) |
| `GROQ_MODEL` | Environment variable | Use a different Groq model (optional) |

To use your own CV, replace `cv.pdf` and update the name and prompt in `app_streamlit.py`.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (never commit `.streamlit/secrets.toml`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app from the repository.
3. Set the main file to `app_streamlit.py`.
4. In Advanced settings, add `GROQ_API_KEY` under Secrets.
5. Click Deploy.

## Author

**Mahmudul**
GitHub: [@mahmudul-eng](https://github.com/mahmudul-eng)
LinkedIn: [add your profile link](https://www.linkedin.com/in/mmahmudul-islam/)
