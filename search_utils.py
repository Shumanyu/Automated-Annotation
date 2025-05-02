import re

def keyword_search(text, keyword, context=40):
    matches = []
    for m in re.finditer(re.escape(keyword), text, re.IGNORECASE):
        start = max(m.start()-context, 0)
        end = m.end()+context
        snippet = text[start:end].replace("\n"," ")
        # Attempt to extract timestamp before match
        ts_match = re.search(r"\[(\d+\.\d+)s\]", text[:m.start()])
        ts = f"{ts_match.group(1)}s" if ts_match else ""
        matches.append((ts, snippet))
    return matches