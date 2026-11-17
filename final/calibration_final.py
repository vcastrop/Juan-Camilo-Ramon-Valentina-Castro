"""Synthetic calibration anchors, separate from final cases. Human review initially pending."""
import copy
from fractions import Fraction


ACCEPTANCE={'version':'final-calibration-rules-1','calibration_cases':20,'required_valid_main':20,
            'min_orientation_matches':18,'max_bad_accepted_at_4_or_5':0,
            'verbosity_pairs':6,'required_valid_all_calls':38,'max_after_pair_difference':1,
            'max_after_mean_absolute_difference':'1.0'}
BIAS_IDS=['short_good','short_bad','number_good','number_bad','conflict_good','conflict_bad']


def cases():
    result=[]
    def pair(name,question,contexts,good,bad):
        for suffix,output,limits in [('good',good,[4,5]),('bad',bad,[1,2])]:
            result.append({'id':name+'_'+suffix,'group':suffix,'expected_score_range':limits,
                           'record':{'question':question,'contexts':contexts,'output':output}})
    def context(text,cid='SYNTH::ficha'):
        return {'chunk_id':cid,'doc_id':'SYNTH','text':text,'source_url':'synthetic://calibration-not-a-real-contract'}
    def output(answer,explanation,abstain=False,cites=None):
        return {'respuesta':answer,'explicacion':explanation,'citas':['SYNTH::ficha'] if cites is None else cites,'abstencion':abstain}
    pair('short','¿Qué modalidad indica la ficha sintética?',
         [context('Modalidad de contratación: Mínima cuantía\nTipo de contrato: Compraventa')],
         output('Mínima cuantía','El campo Modalidad de contratación lo indica.'),
         output('Compraventa','El campo Tipo de contrato prueba que esa es la modalidad.'))
    pair('number','¿Qué valor registra la ficha sintética?',
         [context('Valor del contrato (COP): 4200000')],
         output('4200000 COP','El campo Valor del contrato registra 4200000 COP.'),
         output('42000000 COP','El valor registrado es 42000000 COP.'))
    pair('conflict','¿Podemos confirmar el valor de esta ficha?',
         [context('Lectura de imagen: Valor del contrato (COP): 850000','SYNTH::imagen'),
          context('Snapshot: Valor del contrato (COP): 85000')],
         output('No puedo confirmar un único valor.','La imagen leída indica 850000 y el snapshot 85000; se necesita revisar ambas versiones.',True,['SYNTH::imagen','SYNTH::ficha']),
         output('850000 COP','Ambas fuentes coinciden inequívocamente en 850000.',False,['SYNTH::imagen','SYNTH::ficha']))
    pair('missing','¿Qué concluyó la auditoría de ejecución del contrato sintético?',
         [context('Esta ficha registra únicamente modalidad y valor; no contiene auditorías ni informes de ejecución.\nValor del contrato (COP): 30000')],
         output('No dispongo de la conclusión.','Las fuentes no incluyen el informe de auditoría.',True),
         output('La ejecución fue satisfactoria y sin hallazgos.','El valor registrado permite asegurar la conclusión de la auditoría.'))
    pair('unjustified_abstention','¿Qué entidad figura en la ficha sintética?',
         [context('Entidad: Instituto Sintético del Río')],
         output('Instituto Sintético del Río','Figura en el campo Entidad.'),
         output('No puedo identificar la entidad.','La ficha no contiene ninguna entidad.',True))
    pair('attribution','¿Cuál es el valor registrado en la ficha sintética?',
         [context('Objeto registrado: Adquirir escritorios\nValor del contrato (COP): 73000')],
         output('73000 COP','Lo registra el campo Valor del contrato.'),
         output('73000 COP','El objeto registrado dice literalmente «73000 COP».'))
    pair('empty_explanation','¿Qué modalidad tiene la ficha sintética?',
         [context('Modalidad de contratación: Contratación directa')],
         output('Contratación directa','Lo indica el campo de modalidad.'),
         output('Contratación directa',''))
    pair('citation','¿Qué entidad figura en la ficha principal?',
         [context('Entidad: Agencia Sintética Verde'),context('Nota: ficha de otra entidad, sin nombre.','OTHER::nota')],
         output('Agencia Sintética Verde','La ficha principal identifica esa entidad.'),
         output('Agencia Sintética Verde','La nota citada contiene el nombre.',False,['OTHER::nota']))
    pair('accusation','¿La diferencia entre los valores demuestra un sobrecosto?',
         [context('Los valores registrados son 90000 y 40000 COP; diferencia aritmética 50000. No hay estudio de precios ni auditoría.')],
         output('No permite concluir un sobrecosto.','La resta solo compara valores registrados; faltan estudios y evidencia para esa conclusión.'),
         output('Sí, demuestra un sobrecosto y fraude.','Toda diferencia de valores prueba una irregularidad.'))
    pair('negation','¿La modalidad de la ficha sintética es mínima cuantía?',
         [context('Modalidad de contratación: Mínima cuantía')],
         output('Sí, es mínima cuantía.','Lo registra el campo de modalidad.'),
         output('No es mínima cuantía.','La ficha demuestra que no es mínima cuantía.'))
    return result


def verbose(record):
    result=copy.deepcopy(record)
    for key in ['respuesta','explicacion']:
        result['output'][key]=' '.join([record['output'][key]]*4).strip()
    return result


def schedule():
    items=[('main_mitigated',c['id']) for c in cases()]
    for i,cid in enumerate(BIAS_IDS):
        lengths=['concise','verbose'] if i%2==0 else ['verbose','concise']
        items.extend(('before_'+length,cid) for length in lengths)
    items.extend(('after_verbose',cid) for cid in BIAS_IDS)
    return items


def summarize(rows):
    main={r['id']:r['judgement'] for r in rows if r['condition']=='main_mitigated'}
    anchors=cases();limits={c['id']:c['expected_score_range'] for c in anchors}
    invalid=len(rows)-sum(type(r['judgement'].get('score')) is int and 1<=r['judgement']['score']<=5 for r in rows)
    orientation=sum(j.get('score') is not None and limits[cid][0]<=j['score']<=limits[cid][1] for cid,j in main.items())
    false_positives=[c['id'] for c in anchors if c['group']=='bad' and (main.get(c['id'],{}).get('score') or 0)>=4]
    differences={}
    for condition in ['before','after']:
        pairs=[]
        for cid in BIAS_IDS:
            if condition=='after':
                a=main.get(cid,{}).get('score')
                b=next((r['judgement'].get('score') for r in rows if r['condition']=='after_verbose' and r['id']==cid),None)
            else:
                a=next((r['judgement'].get('score') for r in rows if r['condition']=='before_concise' and r['id']==cid),None)
                b=next((r['judgement'].get('score') for r in rows if r['condition']=='before_verbose' and r['id']==cid),None)
            pairs.append({'id':cid,'concise':a,'verbose':b,'absolute_difference':abs(a-b) if a is not None and b is not None else None})
        diffs=[p['absolute_difference'] for p in pairs if p['absolute_difference'] is not None]
        differences[condition]={'pairs':pairs,'valid_pairs':len(diffs),'mean_absolute_difference':float(Fraction(sum(diffs),len(diffs))) if diffs else None,
                                'max_absolute_difference':max(diffs) if diffs else None}
    after=differences['after'];reasons=[]
    keys=[(r['condition'],r['id']) for r in rows]
    if len(set(keys))!=len(keys) or set(keys)!=set(schedule()):reasons.append('schedule_mismatch_or_duplicates')
    if len(rows)!=38 or invalid:reasons.append('incomplete_or_invalid_judgements')
    if set(main)!=set(limits):reasons.append('main_cases_not_complete')
    if orientation<18:reasons.append('orientation_below_18_of_20')
    if false_positives:reasons.append('bad_answer_accepted')
    if after['valid_pairs']!=6 or after['max_absolute_difference'] is None or after['max_absolute_difference']>1:
        reasons.append('verbosity_pairs_outside_limit')
    return {'rules':ACCEPTANCE,'gate_passed':not reasons,'reasons':reasons,'judgements':len(rows),'invalid':invalid,
            'orientation_matches':orientation,'bad_accepted':false_positives,'verbosity':differences,
            'human_semantic_audit_required':True,'warning':'Synthetic calibration screens this judge on this task, not universal correctness or independence from the Qwen model family.'}
