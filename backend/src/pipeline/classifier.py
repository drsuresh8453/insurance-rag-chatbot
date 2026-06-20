"""
classifier.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Classifies customer questions into 8 query types.
"""
import os
from openai import OpenAI

QUERY_TYPES = ["factual","comparison","summarisation","multi_hop",
               "eligibility","claims_process","calculation","negation"]

PROMPT = """Classify this insurance question into exactly one type:
factual | comparison | summarisation | multi_hop | eligibility | claims_process | calculation | negation

Question: {question}
Return ONLY the type name."""

def classify(question):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp   = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role":"user","content":PROMPT.format(question=question)}])
    raw = resp.choices[0].message.content.strip().lower()
    return raw if raw in QUERY_TYPES else "factual"
