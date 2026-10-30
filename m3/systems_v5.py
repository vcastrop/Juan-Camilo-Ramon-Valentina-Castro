"""Integration candidate: exactly the answer/router protocol tested in the probe."""
import time
from protocol_probe import answer_v5

GENERATOR_ID = 'Qwen/Qwen2.5-3B-Instruct'
GENERATOR_REVISION = 'aa8e72537993ba99e69dfaafa59ed015b17504d1'


def generate_candidate(generator, question, contexts, tools=()):
    # Only inference data; answer_v5 never receives gold/checks/references here.
    result = answer_v5(generator, {'question':question, 'contexts':contexts, 'tools':tools})
    result.update(raw_response=result['answer_attempts'][-1]['raw_response'],
                  parse_error=result['answer_attempts'][-1]['parse_error'])
    return result


class CandidateRAG:
    def __init__(self, retriever, generator, top_k=3):
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be positive integer')
        self.retriever, self.generator, self.top_k = retriever, generator, top_k

    def predict(self, question, retrieve=True):
        if not isinstance(question,str) or not question.strip():
            raise ValueError('Empty question')
        start=time.perf_counter()
        contexts=self.retriever.search(question,self.top_k) if retrieve else []
        retrieval_seconds=time.perf_counter()-start
        result=generate_candidate(self.generator,question,contexts)
        result.update(question=question,contexts=contexts,retrieval_seconds=retrieval_seconds,
                      latency_seconds=time.perf_counter()-start)
        return result
