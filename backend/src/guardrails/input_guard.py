"""
input_guard.py — Author: Suresh D R | AI Product Developer & Technology Mentor
4 safety checks: PII, prompt injection, out-of-scope, length.
PII detection via GPT-4o-mini — no spacy/presidio required.
"""
import re, os
from openai import OpenAI

INJECTION = [
    r"ignore (all )?previous instructions", r"forget (everything|your rules)",
    r"you are now", r"act as", r"jailbreak",
    r"override (your|all) (instructions|rules)", r"disregard your"
]
OUT_SCOPE = [
    r"(write|create) (code|script)",
    r"what is the (capital|population) of",
    r"(weather|stock price|bitcoin)",
    r"(recipe|cook|food)",
    r"(travel|trip|vacation|holiday|tour|flight|hotel booking|itinerary)",
    r"(visa|passport) (application|requirement)",
]
AADHAAR = r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b"
PHONE   = r"\b[6-9]\d{9}\b"
EMAIL   = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def check_pii_with_openai(question):
    """Use GPT-4o-mini to detect PII in question."""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini", temperature=0,
            messages=[{"role": "user", "content":
                f"""Does this text contain any personal information (name, phone, email, ID, Aadhaar, address)?
Text: "{question}"
Reply with only YES or NO."""}])
        return "YES" in resp.choices[0].message.content.upper()
    except:
        return False

def check_input(question):
    if not question.strip():
        return False, "empty", "Please type a question to continue."
    if len(question) > 2000:
        return False, "length", "Please ask one specific question at a time."

    # Regex PII checks (fast, no API call needed)
    if re.search(AADHAAR, question) or re.search(PHONE, question) or re.search(EMAIL, question):
        return False, "pii", "Your question contains personal information. Please remove it and ask again."

    q = question.lower()
    for pat in INJECTION:
        if re.search(pat, q):
            return False, "injection", "Please ask a question about your insurance policy."
    for pat in OUT_SCOPE:
        if re.search(pat, q):
            return False, "scope", "I can only answer questions about your insurance policy."

    # OpenAI PII check for anything regex missed
    if check_pii_with_openai(question):
        return False, "pii", "Your question contains personal information. Please remove it and ask again."

    return True, None, None
