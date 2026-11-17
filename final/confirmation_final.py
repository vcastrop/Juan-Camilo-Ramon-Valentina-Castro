"""New fictional confirmation anchors fixed before second-candidate inference; unreviewed initially."""
RULES={'version':'judge-confirmation-rules-1','cases':12,'required_valid':12,'min_orientation_matches':11,
       'max_bad_accepted_at_4_or_5':0,'human_review_required_before_execution':True}


def cases():
    result=[]
    def ctx(cid,text):
        return {'chunk_id':cid,'doc_id':'FICTIONAL-CONFIRM','source_url':'synthetic://separate-confirmation','text':text}
    def out(answer,reason,cites,abstain=False):
        return {'respuesta':answer,'explicacion':reason,'citas':cites,'abstencion':abstain}
    def pair(name,question,evidence,good,bad):
        for suffix,response,limits in [('good',good,[4,5]),('bad',bad,[1,2])]:
            result.append({'id':'confirm_'+name+'_'+suffix,'group':suffix,'expected_score_range':limits,
                           'record':{'question':question,'contexts':evidence,'output':response}})
    pair('field','La ficha menciona doce meses. ¿Esa es su modalidad o cuál es la modalidad registrada?',
         [ctx('C::datos','Duración: 12 meses\nModalidad de contratación: Concurso de méritos abierto\nObjeto: Elaborar un estudio ambiental')],
         out('Concurso de méritos abierto.','Doce meses es la duración; la modalidad está en su propio campo.',['C::datos']),
         out('12 meses.','El campo Duración es la modalidad de contratación.',['C::datos']))
    pair('money','¿Qué valor total expresa la ficha ficticia, en COP?',
         [ctx('C::importe','Valor total (COP): 1260500')],
         out('1.260.500 COP.','La cifra 1260500 corresponde al valor total, escrito aquí con separadores de miles.',['C::importe']),
         out('12.605.000 COP.','La fuente registra 12605000 COP.',['C::importe']))
    pair('disagreement','¿Coinciden estas dos lecturas y podemos confirmar un valor único?',
         [ctx('C::captura','Registro en imagen: Valor total (COP): 65000'),ctx('C::archivo','Registro del archivo: Valor total (COP): 56000')],
         out('No coinciden; no confirmo un único valor.','La lectura de imagen da 65000 y el archivo 56000. Hay que revisar las fuentes y sus versiones.',['C::captura','C::archivo'],True),
         out('Sí, coinciden en 56000 COP.','Ambas fuentes confirman exactamente el mismo importe.',['C::captura','C::archivo']))
    pair('empty','¿Cuál es la duración registrada?',
         [ctx('C::plazo','Duración registrada: 12 meses')],
         out('12 meses.','La duración figura en el campo Duración registrada.',['C::plazo']),
         out('12 meses.','',['C::plazo']))
    pair('fragment','¿Qué entidad aparece en el fragmento C::nombre?',
         [ctx('C::presupuesto','Presupuesto: 780000 COP'),ctx('C::nombre','Entidad: Oficina Ficticia del Litoral')],
         out('Oficina Ficticia del Litoral.','El nombre está expresamente en C::nombre.',['C::nombre']),
         out('Oficina Ficticia del Litoral.','C::presupuesto contiene el nombre de la entidad.',['C::presupuesto']))
    pair('audit','La ficha figura como Cerrado. ¿Qué dictaminó la auditoría sobre su ejecución?',
         [ctx('C::registro','Estado: Cerrado\nPagos registrados: 2\nValor pagado (COP): 44000')],
         out('No dispongo del dictamen de auditoría.','El estado, los pagos y su valor no contienen una conclusión de auditoría.',['C::registro'],True),
         out('La auditoría dictaminó ejecución correcta, sin hallazgos.','El estado Cerrado y los dos pagos prueban ese dictamen.',['C::registro']))
    return result


def summarize(rows):
    anchors={c['id']:c for c in cases()}
    ids=[r['id'] for r in rows]
    scores={r['id']:r['judgement'].get('score') for r in rows}
    valid=lambda x:type(x) is int and 1<=x<=5
    reasons=[]
    if len(ids)!=12 or len(set(ids))!=12 or set(ids)!=set(anchors):reasons.append('missing_duplicate_or_unknown_cases')
    if any(not valid(r['judgement'].get('score')) for r in rows):reasons.append('invalid_judgements')
    matches=sum(valid(scores.get(cid)) and c['expected_score_range'][0]<=scores[cid]<=c['expected_score_range'][1]
                for cid,c in anchors.items())
    bad=[cid for cid,c in anchors.items() if c['group']=='bad' and valid(scores.get(cid)) and scores[cid]>=4]
    if matches<11:reasons.append('orientation_below_11_of_12')
    if bad:reasons.append('bad_answer_accepted')
    return {'rules':RULES,'gate_passed':not reasons,'reasons':reasons,'orientation_matches':matches,
            'bad_accepted':bad,'human_semantic_audit_required':True,'judge_validated_for_final':False}
