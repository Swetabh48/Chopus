from __future__ import annotations

import math
import re
from collections import Counter


_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text)]


class BM25:
    """Minimal BM25Okapi — local hybrid rerank without extra deps."""

    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(doc) for doc in corpus]
        self.doc_len = [len(doc) or 1 for doc in self.docs]
        self.avgdl = (sum(self.doc_len) / len(self.doc_len)) if self.doc_len else 1.0
        self.doc_freqs: list[Counter[str]] = [Counter(doc) for doc in self.docs]
        self.df: Counter[str] = Counter()
        for freqs in self.doc_freqs:
            for term in freqs:
                self.df[term] += 1
        self.n = len(self.docs)

    def idf(self, term: str) -> float:
        # Standard BM25 idf with +0.5 smoothing
        df = self.df.get(term, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def score(self, query: str, index: int) -> float:
        q_terms = tokenize(query)
        if not q_terms or index >= self.n:
            return 0.0

        freqs = self.doc_freqs[index]
        dl = self.doc_len[index]
        total = 0.0
        for term in q_terms:
            tf = freqs.get(term, 0)
            if tf == 0:
                continue
            denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            total += self.idf(term) * (tf * (self.k1 + 1)) / denom
        return total


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo = min(scores)
    hi = max(scores)
    if hi <= lo:
        return [1.0 if score > 0 else 0.0 for score in scores]
    return [(score - lo) / (hi - lo) for score in scores]


def hybrid_rerank(
    *,
    query: str,
    texts: list[str],
    vector_similarities: list[float],
    vector_weight: float = 0.6,
    top_k: int = 4,
) -> list[int]:
    """Return indices of texts ranked by fused vector + BM25 score."""
    if not texts:
        return []

    bm25 = BM25(texts)
    bm25_raw = [bm25.score(query, i) for i in range(len(texts))]
    bm25_norm = normalize_scores(bm25_raw)
    vec_norm = normalize_scores(vector_similarities)
    lexical_weight = 1.0 - vector_weight

    fused = [
        vector_weight * vec_norm[i] + lexical_weight * bm25_norm[i]
        for i in range(len(texts))
    ]
    ranked = sorted(range(len(texts)), key=lambda i: fused[i], reverse=True)
    return ranked[:top_k]
