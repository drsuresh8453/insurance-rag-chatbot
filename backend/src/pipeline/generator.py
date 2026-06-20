"""
generator.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Generates answers using GPT-4o with the right prompt template per query type.
"""
import os
from pathlib import Path
from openai import OpenAI

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

def load_prompt(name):
    p = PROMPTS_DIR / f"{name}.txt"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def generate_answer(question, top_chunks, query_type):
    client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system  = load_prompt("system_prompt")
    context = "\n\n".join([
        f"[Source: {c.get('section_name','?')} | {c.get('plan_name','')}]\n{c['text']}"
        for c in top_chunks
    ])
    if query_type == "calculation":
        template = load_prompt("calculation")
    elif query_type == "summarisation":
        template = load_prompt("summarisation")
    elif query_type == "comparison":
        template = load_prompt("comparison")
    else:
        template = load_prompt("factual_qa")

    prompt = template.format(system_prompt=system, context=context, question=question)
    resp   = client.chat.completions.create(
        model="gpt-4o", temperature=0.1,
        messages=[{"role":"user","content":prompt}])
    return resp.choices[0].message.content

def generate_suggestions(question):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp   = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.3,
        messages=[{"role":"user","content":
            f'Customer asked: "{question}". Suggest 3 short follow-up insurance questions as JSON list only.'}])
    try:    return __import__("json").loads(resp.choices[0].message.content)
    except: return []
