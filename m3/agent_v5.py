"""Bounded agent using the probed v5 router and common v5 response protocol."""
import json
import time
from contract_tools import TOOL_SCHEMA
from retrieval_advanced import ids_in
from agent_v4 import normalize_decision
from protocol_probe import ROUTER_V5
from systems_v5 import generate_candidate


class CandidateAgent:
    def __init__(self, retriever, generator, tools, top_k=3, max_steps=3):
        if type(max_steps) is not int or not 1 <= max_steps <= 3:
            raise ValueError('Require 1..3 controller steps')
        self.retriever, self.generator, self.tools = retriever, generator, tools
        self.top_k, self.max_steps = top_k, max_steps

    def predict(self, question):
        if not isinstance(question,str) or not question.strip():
            raise ValueError('Empty question')
        start = time.perf_counter()
        contexts = list(self.retriever.search(question,self.top_k))
        retrieved = list(contexts)
        retrieval_seconds = time.perf_counter()-start
        trace, successes, seen, feedback = [], [], set(), None
        termination = 'max_steps'
        calls = 0
        for step in range(self.max_steps):
            # Routing depends on user request, not distracting chunks/labels/gold.
            payload = {'pregunta': question, 'ids_en_pregunta': sorted(ids_in(question)),
                       'herramienta': TOOL_SCHEMA, 'pasos_restantes': self.max_steps-step}
            if feedback:
                payload['error_anterior'] = feedback
            raw = self.generator.generate(ROUTER_V5, json.dumps(payload,ensure_ascii=False))
            event = {'step':step+1,'raw_response':raw,'decision':None,'normalization':None,
                     'parse_error':None,'tool_result':None,
                     'generation':dict(getattr(self.generator,'last_generation',{}))}
            trace.append(event)
            try:
                decision, normalization = normalize_decision(raw)
                event.update(decision=decision, normalization=normalization)
            except (ValueError,TypeError) as exc:
                feedback = event['parse_error'] = str(exc)
                continue
            if decision['action']=='answer':
                termination='model_answer'
                break
            key=json.dumps([decision['name'], decision['arguments']],sort_keys=True)
            if key in seen:
                event['tool_result']={'ok':False,'error':'Duplicate call blocked','contexts':[]}
                termination='duplicate_call'
                break
            seen.add(key)
            calls += 1
            result=self.tools.execute(decision['name'],decision['arguments'],ids_in(question))
            event['tool_result']=result
            if result['ok']:
                successes.append(result)
                known={c['chunk_id'] for c in contexts}
                contexts.extend(c for c in result['contexts'] if c['chunk_id'] not in known)
                # One bounded tool solves this operation; do not ask model to repeat it.
                termination='tool_success'
                break
            feedback=result['error']
        result=generate_candidate(self.generator,question,contexts,successes)
        result.update(question=question, contexts=contexts,retrieved_contexts=retrieved,
                      retrieval_seconds=retrieval_seconds,latency_seconds=time.perf_counter()-start,
                      tool_trace=trace,termination=termination,tool_calls=calls)
        return result
