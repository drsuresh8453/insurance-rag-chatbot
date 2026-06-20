"""
hallucination.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Verifies every claim in the answer is supported by retrieved chunks.
"""
import os
from openai import OpenAI

PROMPT = """You are a fact-checker for an insurance AI assistant.
Document excerpts given:
{context}

Assistant answer:
{answer}

Is every factual claim supported by the excerpts?
Reply:
VERDICT: SUPPORTED or UNSUPPORTED
REASON: (brief)"""

def check_hallucination(answer, chunks):
    client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    context = "\n\n".join([f"[Chunk {i+1}]: {c['text']}" for i,c in enumerate(chunks)])
    resp    = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role":"user","content":PROMPT.format(context=context,answer=answer)}])
    text    = resp.choices[0].message.content
    verdict = "UNSUPPORTED" if "UNSUPPORTED" in text.upper() else "SUPPORTED"
    reason  = next((l.replace("REASON:","").strip() for l in text.split("\n") if "REASON:" in l),"")
    return verdict == "SUPPORTED", verdict, reason
