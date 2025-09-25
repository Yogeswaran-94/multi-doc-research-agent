# app.py
import streamlit as st
import os
from agent.loader import load_from_path, chunk_docs
from agent.vectorstore import SimpleFAISSStore
from agent.retriever import retrieve
from agent.planner import create_plan
from agent.generator import generate_answer
from langchain.docstore.document import Document
import json
import tempfile

st.set_page_config(page_title="Multi-Document Research Agent", layout="wide")

st.title("📚 Multi-Document Research Agent (RAG + Planning)")
st.write("Ask a complex question. The agent will search local files + web, retrieve top-k chunks, and synthesize a structured report with citations.")

# --- left pane: upload / load local docs ---
st.sidebar.header("Local documents / index")
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

uploaded = st.sidebar.file_uploader("Upload a PDF / TXT / MD file (optional)", type=["pdf","txt","md"])
if uploaded:
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1])
    tf.write(uploaded.getvalue())
    tf.flush()
    st.sidebar.success(f"Saved {uploaded.name} to temp and will be added to index.")
    add_path = tf.name
else:
    add_path = None

# Load or build vectorstore
store = SimpleFAISSStore()
loaded = store.load()
if not loaded:
    # try to load all files from data folder
    docs = load_from_path(data_dir)
    if docs:
        chunks = chunk_docs(docs)
        store.build(chunks)
        st.sidebar.success(f"Built vector index from {len(chunks)} chunks in '{data_dir}'.")
    else:
        st.sidebar.info("No local docs found in data/ — you can upload a file on the left or drop sample docs into data/")

# If user uploaded one file, load & add it
if add_path:
    try:
        docs2 = load_from_path(add_path)
        chunks2 = chunk_docs(docs2)
        store.add_documents(chunks2)
        st.sidebar.success(f"Added uploaded file ({uploaded.name}) to index with {len(chunks2)} chunks.")
    except Exception as e:
        st.sidebar.error(f"Failed to add uploaded file: {e}")

# --- main UI ---
question = st.text_area("Enter your research question:", height=120)

col1, col2 = st.columns([2,1])

with col2:
    k = st.number_input("Top-k local results", value=5, min_value=1, max_value=10)
    synth_button = st.button("Generate Answer")

if synth_button:
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    # 1) Plan
    plan = create_plan(question)
    st.subheader("🧭 Reasoning Plan")
    for step in plan:
        st.write("- " + step)

    # 2) Retrieve
    st.subheader("🔎 Retrieved (local + web)")
    hits = retrieve(question, store, top_k=k)
    for i, h in enumerate(hits, start=1):
        st.markdown(f"**{i}. (Source: {h.get('source')})**")
        st.write(h.get("text") or h.get("text_snippet"))

    # 3) Synthesize
    st.subheader("✅ Final structured report")
    with st.spinner("Generating final report..."):
        final_md = generate_answer(question, hits, plan)
    st.markdown(final_md)

    # 4) Export
    if st.button("Export report as JSON"):
        out = {
            "question": question,
            "plan": plan,
            "hits": hits,
            "report_markdown": final_md
        }
        fname = "report.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        st.success(f"Saved {fname} — download from the app folder.")
