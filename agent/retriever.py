# agent/retriever.py
import wikipedia

def retrieve(query: str, store, top_k: int = 5):
    """
    store: SimpleFAISSStore instance (from agent.vectorstore)
    Returns: list of hits (ordered) each as dict {"text":..., "source":..., "score":...}
    """
    hits = []
    # local top-k
    try:
        local = store.query(query, k=top_k)
        for item in local:
            hits.append({
                "text": item.get("text_snippet", ""),
                "source": item.get("source", "Local Document"),
                "score": item.get("score", 0.0)
            })
    except Exception:
        pass

    # Wikipedia fallback summary (single short item)
    try:
        wiki_summary = wikipedia.summary(query, sentences=3)
        if wiki_summary:
            hits.append({
                "text": wiki_summary,
                "source": "Wikipedia",
                "score": None
            })
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            # try first option
            wiki_summary = wikipedia.summary(e.options[0], sentences=3)
            hits.append({"text": wiki_summary, "source": "Wikipedia", "score": None})
        except Exception:
            pass
    except Exception:
        pass

    return hits
