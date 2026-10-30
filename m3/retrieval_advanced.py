"""BM25+dense/RRF, explicit ID filtering, and optional cross-encoder reranking.

ID constraints come exclusively from the user question, never from gold labels.
"""
import re
import unicodedata


def ids_in(text):
    return set(re.findall(r'CO1\.PCCNTR\.\d+\b', text.upper()))


def tokens(text):
    text = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if not unicodedata.combining(c))
    return re.findall(r'co1\.pccntr\.\d+|\w+', text)


def rrf(rankings, constant=60):
    if constant <= 0:
        raise ValueError('RRF constant must be positive')
    scores = {}
    for ranking in rankings:
        seen = set()
        for rank, cid in enumerate(ranking, 1):
            if cid not in seen:
                scores[cid] = scores.get(cid, 0) + 1 / (constant + rank)
                seen.add(cid)
    return sorted(scores, key=lambda cid: (-scores[cid], cid)), scores


class HybridRetriever:
    def __init__(self, dense, chunks, candidate_count=12):
        from rank_bm25 import BM25Okapi
        self.dense, self.chunks, self.candidate_count = dense, chunks, candidate_count
        self.by_id = {c['chunk_id']: c for c in chunks}
        self.bm25 = BM25Okapi([tokens(c['doc_id']+'\n'+c['text']) for c in chunks])

    def search(self, question, k):
        wanted = ids_in(question)
        eligible = [c for c in self.chunks if not wanted or c['doc_id'].upper() in wanted]
        if not eligible:
            return []
        allowed = {c['chunk_id'] for c in eligible}
        n = max(k, self.candidate_count)
        # Retrieve all dense scores for this small corpus before applying ID restriction.
        # Larger corpora should push this filter down to the vector store.
        dense = [c for c in self.dense.search(question, len(self.chunks)) if c['chunk_id'] in allowed][:n]
        scores = self.bm25.get_scores(tokens(question))
        indices = sorted(range(len(self.chunks)), key=lambda i: (-float(scores[i]), self.chunks[i]['chunk_id']))
        sparse = [self.chunks[i]['chunk_id'] for i in indices if self.chunks[i]['chunk_id'] in allowed][:n]
        ranked, fused = rrf([[c['chunk_id'] for c in dense], sparse])
        return [dict(self.by_id[cid], rrf_score=fused[cid]) for cid in ranked[:k]]


class RerankedRetriever:
    def __init__(self, hybrid, scorer, candidate_count=12):
        self.hybrid, self.scorer, self.candidate_count = hybrid, scorer, candidate_count

    def search(self, question, k):
        candidates = self.hybrid.search(question, max(k, self.candidate_count))
        if not candidates:
            return []
        pairs = [(question, c['doc_id']+'\n'+c['text']) for c in candidates]
        scores = self.scorer.predict(pairs)
        if len(scores) != len(candidates):
            raise ValueError('Reranker score count mismatch')
        ordered = sorted(zip(scores, candidates), key=lambda item: (-float(item[0]), item[1]['chunk_id']))
        return [dict(c, rerank_score=float(score)) for score, c in ordered[:k]]
