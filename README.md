# Multi-Document Research Agent (RAG + Planning)

## Author
Yogeswaran S
(yogeswaran00794@gmail.com)

## Project Overview
This project is an **AI research assistant** that answers complex questions by retrieving and synthesizing information from both **local documents** and the **web**. It demonstrates **Retrieval-Augmented Generation (RAG)** with **multi-step reasoning**, vector embeddings, and structured output with citations.

**Example Question:**  
*Explain how quantum computing affects cybersecurity and propose mitigation strategies.*
The system produces a **structured answer** with **bullet points**, **citations**, and a **traceable reasoning plan**.

## Features
- ✅ Accepts **natural language questions** from the user  
- ✅ Retrieves relevant information from **local documents** (PDFs/Markdown)  
- ✅ Searches **web sources** (e.g., Wikipedia) for additional context  
- ✅ Implements **multi-step reasoning**: `Plan → Retrieve → Synthesize`  
- ✅ Uses **vectorization & embeddings** for semantic search  
- ✅ Produces **structured Markdown or JSON reports** with citations  
- ✅ Fully interactive **Streamlit UI** for querying  


## Project Structure
multi-doc-research-agent/
1. agent/ – Core modules of the agent
* generator.py – Summarizes documents & generates answers
* loader.py – Loads PDFs/TXT/MD files and chunks them
* planner.py – Defines multi-step reasoning plan
* retriever.py – Retrieves top-k chunks from local + Wikipedia
* vectorstore.py – Builds and loads FAISS vectorstore
2. data/ – Document repository
* quantum_computing.pdf
* post_quantum.pdf
* ai_cybersecurity.pdf
4. app.py – Streamlit interface for user interaction
5. README.md – Project documentation
6. faiss.index – FAISS vectorstore index (auto-generated)
7. faiss_meta.json – Metadata for FAISS vectorstore
8. requirements.txt - project dependencies

## Installation
1. Clone the repository:
git clone https://github.com/Yogeswaran-94/multi-doc-research-agent.git
cd multi-doc-research-agent

2. Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate     

3. Install dependencies:
pip install -r requirements.txt

4. Set your OpenAI API key as an environment variable:
setx OPENAI_API_KEY "sk-your-api-key"     

5. Run the Streamlit app:
streamlit run app.py

Enter a natural language question in the input box.
The agent will:
1. Show the reasoning plan
2. Retrieve relevant chunks from local + web sources
3. Generate a structured Markdown answer with citations
Optionally, export the answer as JSON.

Example Output
Question:
Explain how quantum computing affects cybersecurity and propose mitigation strategies.

Plan:
Identify impact of quantum computing on current encryption
Retrieve relevant documents from local + Wikipedia
Synthesize information into bullet points with citations

Answer:
Quantum computers can break classical encryption algorithms. (Source: data/sample_cybersecurity.md)
Post-quantum cryptography is a mitigation approach. (Source: Wikipedia: Quantum Cryptography)
Hybrid encryption methods can help transition securely. (Source: data/sample_quantum.pdf)

## Deployment
Deploy for free on Streamlit Community Cloud:
1. Push this repository to GitHub
2. Log in to Streamlit Community Cloud
3. Create a new app, select your repo, branch (main) and file (app.py)
4. Set your OpenAI API key as a secret

## Skills Demonstrated
Retrieval-Augmented Generation (RAG),
Multi-step reasoning & agent planning,
Semantic search using vector embeddings,
Prompt engineering for summarization & citations,
Interactive Streamlit application development.