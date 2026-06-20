"""
decomposer.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Decomposes multi-hop questions into simple sub-questions.
"""
import os, json
from openai import OpenAI

PROMPT = """Insurance question: "{question}"
Break into 2-4 simple sub-questions each targeting ONE policy section.
Return as JSON list only. No explanation."""

def decompose(question):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp   = client.chat.completions.create(
        model="gpt-4o", temperature=0,
        messages=[{"role":"user","content":PROMPT.format(question=question)}])
    try:    return json.loads(resp.choices[0].message.content)
    except: return [question]
