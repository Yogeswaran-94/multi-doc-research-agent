# agent/generator.py
import os
import json
from typing import List, Dict

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def _build_prompt(question: str, hits: List[Dict], plan: List[str]) -> str:
    # Compose context lines with explicit sources
    context_lines = []
    for i, h in enumerate(hits, 1):
        snippet = h.get("text") or h.get("text_snippet") or ""
        source = h.get("source", "Local")
        context_lines.append(f"[{i}] Source: {source}\n{snippet}\n")

    prompt = f"""
You are an expert research assistant. Follow this plan: {json.dumps(plan, indent=2)}

Question: {question}

Context (top relevant chunks):
{"".join(context_lines)}

Produce a clear, concise structured report in Markdown with:
- A short executive summary (1-2 bullets)
- Key findings as bullet points (each bullet must include a short parenthetical citation like (Source: ...))
- Suggested mitigation / recommendations (bulleted)
- A final 'Traceability' section listing each claim and its source (mapping from bullet -> source)

Use no more than ~600 words. Be precise and tag each claim with its source.
"""
    return prompt

def generate_answer(question: str, hits: List[Dict], plan: List[str]) -> str:
    """
    Returns Markdown string. If OPENAI_API_KEY exists, uses OpenAI chat completion.
    Otherwise uses a simple heuristic summary fallback.
    """
    prompt = _build_prompt(question, hits, plan)

    # If OpenAI key exists, use it for better synthesis
    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            # Use ChatCompletion (gpt-3.5-turbo) — adjust model if needed
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            text = resp["choices"][0]["message"]["content"]
            return text
        except openai.error.RateLimitError as e:
            # propagate message about quota to user-friendly output
            return f"**OpenAI rate/quotas error:** {str(e)}\n\nFalling back to local summarizer below.\n\n" + _fallback_summary(question, hits, plan)
        except Exception as e:
            return f"**OpenAI generation error:** {str(e)}\n\nFalling back to local summarizer below.\n\n" + _fallback_summary(question, hits, plan)
    else:
        return _fallback_summary(question, hits, plan)

def _fallback_summary(question: str, hits: List[Dict], plan: List[str]) -> str:
    """
    Very simple local summarizer: extracts sentences that contain keywords from the question.
    Not as fluent as LLM but safe if no OpenAI key.
    """
    import re
    q_tokens = re.findall(r"\w+", question.lower())
    bullets = []
    for h in hits:
        text = h.get("text") or h.get("text_snippet") or ""
        # pick sentence with most token overlap
        sentences = re.split(r'(?<=[.!?])\s+', text)
        best = ""
        best_score = 0
        for s in sentences:
            s_low = s.lower()
            score = sum(1 for t in q_tokens if t in s_low)
            if score > best_score and len(s.strip())>10:
                best = s.strip()
                best_score = score
        if not best and sentences:
            best = sentences[0].strip()
        source = h.get("source","Local")
        bullets.append(f"- {best} (Source: {source})")
    # Compose simple markdown
    md = f"## Executive summary\n\n- {question}\n\n## Key findings\n\n"
    md += "\n".join(bullets[:10])
    md += "\n\n## Recommendations\n\n- Review the above findings and consult original sources.\n\n## Traceability\n\n"
    for i, h in enumerate(hits,1):
        md += f"- Claim {i}: Source: {h.get('source','Local')}\n"
    return md
