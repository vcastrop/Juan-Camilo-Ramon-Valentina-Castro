"""Frozen M3 systems as `sistema(pregunta) -> registro`, the interface the harness calls.

Configuration = integration v5 (audited), without changes: same generator, ANSWER_V5 prompt,
generation parameters and index for every row. Only retrieval and the tool layer change.
"""
from agent_v5 import CandidateAgent
from contract_tools import ContractTools
from retrieval_advanced import HybridRetriever, RerankedRetriever
from systems_v5 import CandidateRAG

CONFIG = {
    'config_version': 'm3-final-1.0 (= integración v5 congelada)',
    'chunk_chars': 220, 'overlap_chars': 30, 'identity_in_embeddings': True,
    'top_k': 3, 'candidate_count': 12, 'rrf_constant': 60, 'max_controller_steps': 3,
    'max_new_tokens': 512, 'decoding': 'greedy (do_sample=False)', 'seed': 42,
}
# Main table rows, then ablations (one technique at a time) for "qué movió qué".
MAIN = ['sin_rag', 'rag_ingenuo', 'rag_avanzado', 'sistema_final']
ABLATIONS = ['ablacion_solo_hibrido', 'ablacion_denso_rerank']
LABELS = {
    'sin_rag': 'Línea base sin RAG (mismo generador; adaptación de M2)',
    'rag_ingenuo': 'RAG ingenuo (S07): denso top-3',
    'rag_avanzado': 'RAG avanzado: híbrido BM25+denso RRF con filtro de ID + reranking',
    'sistema_final': 'Sistema final: avanzado + herramienta (agente acotado)',
    'ablacion_solo_hibrido': 'Ablación: híbrido RRF con filtro de ID, sin reranking',
    'ablacion_denso_rerank': 'Ablación: denso + reranking, sin híbrido',
}


def construir(dense, chunks, scorer, generator, documents):
    """Build every variant from shared components (real models or test doubles)."""
    k, n = CONFIG['top_k'], CONFIG['candidate_count']
    hybrid = HybridRetriever(dense, chunks, candidate_count=n)
    advanced = RerankedRetriever(hybrid, scorer, candidate_count=n)
    systems = {
        'sin_rag': CandidateRAG(dense, generator, k),
        'rag_ingenuo': CandidateRAG(dense, generator, k),
        'rag_avanzado': CandidateRAG(advanced, generator, k),
        'sistema_final': CandidateAgent(advanced, generator, ContractTools(documents), k,
                                        CONFIG['max_controller_steps']),
        'ablacion_solo_hibrido': CandidateRAG(hybrid, generator, k),
        'ablacion_denso_rerank': CandidateRAG(RerankedRetriever(dense, scorer, n), generator, k),
    }

    def wrap(name):
        system = systems[name]
        if name == 'sin_rag':
            return lambda pregunta: dict(system.predict(pregunta, retrieve=False), variant=name)
        return lambda pregunta: dict(system.predict(pregunta), variant=name)

    return {name: wrap(name) for name in systems}


_SISTEMAS = {}


def inicializar(dense, chunks, scorer, generator, documents):
    _SISTEMAS.update(construir(dense, chunks, scorer, generator, documents))


def sistema_sin_rag(pregunta):
    return _SISTEMAS['sin_rag'](pregunta)


def sistema_rag(pregunta):
    return _SISTEMAS['rag_ingenuo'](pregunta)


def sistema_rag_avanzado(pregunta):
    return _SISTEMAS['rag_avanzado'](pregunta)


def sistema_final(pregunta):
    return _SISTEMAS['sistema_final'](pregunta)
