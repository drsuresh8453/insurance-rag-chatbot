"""
output_guard.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Post-generation checks: citation, disclaimer, hallucination gate.
"""
MEDICAL_DISCLAIMER = (
    "\n\n*This information is based on your policy document. "
    "For medical decisions, consult a qualified doctor. "
    "Final claim approval is subject to policy terms and medical assessment.*"
)

def check_output(answer, query_type, is_grounded):
    issues = []
    citation_words = ["section","clause","policy","as per","according to"]
    if not any(w in answer.lower() for w in citation_words):
        answer += "\n\n*Please refer to your policy document for the exact clause.*"
        issues.append("no_citation")
    if query_type in ["factual","eligibility","multi_hop","calculation"]:
        if MEDICAL_DISCLAIMER not in answer:
            answer += MEDICAL_DISCLAIMER
    if not is_grounded:
        answer += "\n\n*Note: This answer could not be fully verified against policy documents. Please confirm with your advisor.*"
        issues.append("hallucination_warning")
    return answer, issues
