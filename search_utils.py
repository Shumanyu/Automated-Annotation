import re
from bisect import bisect_right

TIMESTAMP_RE = re.compile(r"\[(\d+\.\d+)s\]")


def keyword_search(text, keyword, context=40):
    """Find keyword occurrences, tagged with the timestamp they fall under.

    Returns a list of (timestamp, snippet) tuples.
    """
    if not keyword or not keyword.strip():
        return []

    # Index every timestamp marker once, so each hit can binary-search the
    # nearest preceding one. Scanning text[:pos] per hit (as this used to)
    # returns the *first* timestamp in the document rather than the enclosing
    # segment's, so every result reported the same time.
    stamps = [(m.start(), m.group(1)) for m in TIMESTAMP_RE.finditer(text)]
    positions = [pos for pos, _ in stamps]

    matches = []
    for m in re.finditer(re.escape(keyword), text, re.IGNORECASE):
        start = max(m.start() - context, 0)
        end = m.end() + context
        snippet = text[start:end].replace("\n", " ")
        idx = bisect_right(positions, m.start()) - 1
        ts = f"{stamps[idx][1]}s" if idx >= 0 else ""
        matches.append((ts, snippet))
    return matches
