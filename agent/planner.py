# agent/planner.py

def create_plan(question: str):
    """
    Return a structured plan (list of strings) for the agent.
    """
    return [
        "Analyze the question and break it into sub-questions",
        "Retrieve top-k relevant chunks from local documents (FAISS) and web (Wikipedia)",
        "Summarize each retrieved chunk and attach its source",
        "Synthesize the summaries into a final structured report with citations"
    ]
