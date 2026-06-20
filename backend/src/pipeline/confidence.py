"""
confidence.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Computes confidence score from 4 signals: similarity, rerank, hallucination, query type.
"""
TYPE_MODS = {
    "factual":0,"eligibility":0,"claims_process":0,
    "negation":-0.05,"comparison":-0.05,"summarisation":-0.05,
    "calculation":-0.10,"multi_hop":-0.10,
}

def compute_confidence(sims, reranks, is_grounded, query_type):
    avg_sim     = sum(sims)/len(sims) if sims and any(s>0 for s in sims) else 0.6
    top_rerank  = reranks[0] if reranks and reranks[0] != 0 else 5.0
    rerank_norm = min(max((top_rerank+10)/20,0),1)
    hall_pen    = 0 if is_grounded else -0.30
    type_mod    = TYPE_MODS.get(query_type, 0)
    score = round(min(max((avg_sim*0.5)+(rerank_norm*0.45)+hall_pen+type_mod,0),1),2)
    if   score >= 0.75: cat, flag = "HIGH",   False
    elif score >= 0.50: cat, flag = "MEDIUM", False
    else:               cat, flag = "LOW",    True
    return {"score":score,"category":cat,"flag":flag,
            "breakdown":{"similarity":round(avg_sim,2),"rerank_norm":round(rerank_norm,2),
                         "hall_penalty":hall_pen,"type_mod":type_mod}}
