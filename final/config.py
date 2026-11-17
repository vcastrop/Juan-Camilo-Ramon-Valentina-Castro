"""Pinned development integration; not an accepted efficiency configuration."""
MODELS = {
    'embedding': ('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', 'e8f8c211226b894fcb81acc59f3b34ba3efd5f42'),
    'generator': ('Qwen/Qwen2.5-3B-Instruct', 'aa8e72537993ba99e69dfaafa59ed015b17504d1'),
    'reranker': ('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1', '1427fd652930e4ba29e8149678df786c240d8825'),
    'vision': ('Qwen/Qwen2-VL-2B-Instruct', '895c3a49bc3fa70a340399125c650a463535e71c'),
    'classifier': ('BSC-LT/RoBERTalex', '2a1c89fd468a362368463b4126751fdd51c4d847'),
}
VERSION = 'final-integration-dev-0.3'
SEED = 42
