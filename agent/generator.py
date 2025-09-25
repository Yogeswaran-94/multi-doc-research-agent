# agent/generator.py
import os
import json
from typing import List, Dict

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def _build_prompt(question: str, hits: List[Dict], plan: List[str]) -> str:
    """Builds the LLM prompt with context and plan."""
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
    Returns Markdown string.
    If OPENAI_API_KEY exists, uses OpenAI ChatCompletion.
    Otherwise, uses a simple local summarizer.
    """
    prompt = _build_prompt(question, hits, plan)

    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            text = resp["choices"][0]["message"]["content"]
            return text

        except Exception:
            # Silently fallback to local summarizer
            return _fallback_summary(question, hits, plan)
    else:
        return _fallback_summary(question, hits, plan)


def _fallback_summary(question: str, hits: List[Dict], plan: List[str]) -> str:
    """
    Local summarizer: extracts sentences with keyword overlap
    and formats into a structured Markdown report.
    """
    import re
    q_tokens = re.findall(r"\w+", question.lower())
    bullets = []
    for h in hits:
        text = h.get("text") or h.get("text_snippet") or ""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        best = ""
        best_score = 0
        for s in sentences:
            s_low = s.lower()
            score = sum(1 for t in q_tokens if t in s_low)
            if score > best_score and len(s.strip()) > 10:
                best = s.strip()
                best_score = score
        if not best and sentences:
            best = sentences[0].strip()
        source = h.get("source", "Local")
        bullets.append(f"- {best} (Source: {source})")

    # Build structured Markdown report
    md = ""
    md += "## Executive summary\n\n"
    md += f"- Core research question: {question}\n\n"
    md += "## Key findings\n\n"
    md += "\n".join(bullets[:10])
    md += "\n\n## Recommendations\n\n"
    md += "- Review the above findings and consult original sources.\n"
    md += "- Consider domain-specific mitigation strategies.\n"
    md += "\n## Traceability\n\n"
    for i, h in enumerate(hits, 1):
        md += f"- Claim {i}: Source: {h.get('source','Local')}\n"
    return md
