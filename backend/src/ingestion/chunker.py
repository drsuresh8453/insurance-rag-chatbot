"""
chunker.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Section-type-aware chunking strategy.
Tables never split. Exclusions/defs: 400 chars. General: 700 chars.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

SMALL  = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50,  separators=["\n\n","\n",". "," "])
MEDIUM = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100, separators=["\n\n","\n",". "," "])

def detect_section_type(section_name):
    s = section_name.lower()
    if any(k in s for k in ["exclusion","not covered","what is not"]): return "exclusion"
    if any(k in s for k in ["definition","meaning","terms"]):           return "definition"
    if any(k in s for k in ["coverage","what is covered","benefit"]):   return "coverage"
    if any(k in s for k in ["claim","procedure","how to"]):             return "claims"
    if any(k in s for k in ["waiting","wait"]):                         return "waiting_period"
    if any(k in s for k in ["co-payment","copayment","deductible"]):    return "copayment"
    if any(k in s for k in ["grievance","complaint"]):                  return "grievance"
    return "general"

def chunk_document(fname, paragraphs, tables, meta):
    chunks, chunk_id = [], 0
    for table in tables:
        chunk_id += 1
        chunks.append({
            "chunk_id": f"{meta['doc_id']}-chunk-{chunk_id:04d}",
            "text": table["table_text"], "chunk_type": "table",
            "section_name": f"Table {table['table_index']+1}",
            "source_file": fname, **meta,
            "char_count": len(table["table_text"]),
            "word_count": len(table["table_text"].split()),
        })
    current_section, current_texts = None, []

    def flush(sname, texts, stype, cid):
        new_c = []
        combined = " ".join(texts)
        if not combined.strip(): return new_c, cid
        splitter = SMALL if stype in ["exclusion","definition"] else MEDIUM
        for part in splitter.split_text(combined):
            if len(part.strip()) < 60: continue
            cid += 1
            new_c.append({
                "chunk_id": f"{meta['doc_id']}-chunk-{cid:04d}",
                "text": part.strip(), "chunk_type": stype,
                "section_name": sname, "source_file": fname, **meta,
                "char_count": len(part), "word_count": len(part.split()),
            })
        return new_c, cid

    for para in paragraphs:
        if not para["text"]: continue
        if para["section_name"] != current_section:
            if current_section and current_texts:
                stype = detect_section_type(current_section)
                nc, chunk_id = flush(current_section, current_texts, stype, chunk_id)
                chunks.extend(nc)
            current_section, current_texts = para["section_name"], [para["text"]]
        else:
            current_texts.append(para["text"])
    if current_section and current_texts:
        stype = detect_section_type(current_section)
        nc, chunk_id = flush(current_section, current_texts, stype, chunk_id)
        chunks.extend(nc)
    return chunks
