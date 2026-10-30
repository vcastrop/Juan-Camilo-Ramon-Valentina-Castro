"""Synthetic judge calibration and 12 verbosity pairs; expectations never enter judge."""
import copy
import statistics


def calibration_cases():
    cases=[]
    fields=[('modalidad','Modalidad de contratación','Selección abreviada','Compraventa'),
            ('entidad','Entidad','Entidad sintética Norte','Entidad sintética Sur'),
            ('valor','Valor del contrato (COP)','12000','120000'),
            ('duración','Duración registrada','6 meses','60 meses')]
    for i,(field,title,right,wrong) in enumerate(fields):
        cid=f'CAL-G-{i}'
        context={'chunk_id':cid,'doc_id':cid,'text':f'{title}: {right}', 'source_url':'synthetic://judge-calibration'}
        question=f'¿Qué {field} figura en la ficha sintética?'
        for kind,answer,reason,limits in [
            ('supported',right,f'El campo {title} registra {right}.',[4,5]),
            ('wrong',wrong,f'El campo {title} registra {wrong}.',[1,2])]:
            # One wrong case deliberately has no explanation, reproducing professor's concern.
            if kind=='wrong' and i==0:
                reason=''
            cases.append({'id':f'{kind}_{i}','group':kind,'expected_range_for_review':limits,
                          'record':{'question':question,'contexts':[context],
                                    'output':{'respuesta':answer,'explicacion':reason,
                                              'citas':[cid],'abstencion':False}}})
    for i,missing in enumerate(['informe de auditoría','cláusula de multas','informe de ejecución física','estudio de precios de mercado']):
        cid=f'CAL-A-{i}'
        cases.append({'id':f'abstention_{i}','group':'abstention','expected_range_for_review':[4,5],
                      'record':{'question':f'¿Qué dice el {missing} del contrato sintético?',
                                'contexts':[{'chunk_id':cid,'doc_id':cid,'source_url':'synthetic://judge-calibration',
                                             'text':f'Estado: Cerrado. Esta ficha resumida no contiene {missing}.'}],
                                'output':{'respuesta':f'No dispongo del {missing} en estas fuentes.',
                                          'explicacion':'La ficha no incluye ese documento; no puedo afirmar su contenido.',
                                          'citas':[cid],'abstencion':True}}})
    return cases


def verbose_equivalent(record):
    result=copy.deepcopy(record)
    # Literal repetition adds length without claims, confidence or extra evidence.
    for key in ['respuesta','explicacion']:
        result['output'][key]=' '.join([record['output'][key]]*4).strip()
    return result


def summarize_calibration(rows):
    from judge import summarize_judgements
    summaries={}
    for condition in ['before','after']:
        subset=[r for r in rows if r['condition']==condition]
        by_key={(r['case_id'],r['length']):r for r in subset}
        comparisons=[]
        for cid in sorted({r['case_id'] for r in subset}):
            a=by_key.get((cid,'concise')); b=by_key.get((cid,'verbose'))
            sa=a['judgement']['score'] if a else None
            sb=b['judgement']['score'] if b else None
            comparisons.append({'case_id':cid,'concise':sa,'verbose':sb,
                                'signed_difference':sb-sa if sa is not None and sb is not None else None})
        valid=[p['signed_difference'] for p in comparisons if p['signed_difference'] is not None]
        concise=[r for r in subset if r['length']=='concise']
        orientation=[r for r in concise if r['judgement']['score'] is not None]
        match=sum(r['expected_range_for_review'][0]<=r['judgement']['score']<=r['expected_range_for_review'][1] for r in orientation)
        summaries[condition]={'judgements':summarize_judgements([r['judgement'] for r in subset]),
                              'pairs_total':len(comparisons),'pairs_valid':len(valid),
                              'mean_signed_difference':statistics.mean(valid) if valid else None,
                              'mean_absolute_difference':statistics.mean(map(abs,valid)) if valid else None,
                              'max_absolute_difference':max(map(abs,valid)) if valid else None,
                              'pairs_with_difference_over_one':sum(abs(x)>1 for x in valid),
                              'orientation_total':len(concise),'orientation_valid':len(orientation),
                              'orientation_expected_range_matches':match,
                              'pairs':comparisons,'human_semantic_review_required':True}
    return summaries


def evaluate_calibration(generator, emit, judge_factory=None):
    from judge import IndependentJudge
    cases=calibration_cases()
    rows=[]
    for condition in ['before','after']:
        judge=(judge_factory or IndependentJudge)(generator,mitigate_verbosity=(condition=='after'))
        for i,case in enumerate(cases):
            # Alternate ordering; each judgement is independent, without conversation history.
            lengths=['concise','verbose'] if i%2==0 else ['verbose','concise']
            for length in lengths:
                record=case['record'] if length=='concise' else verbose_equivalent(case['record'])
                judgement=judge.evaluate(record)
                row={'condition':condition,'case_id':case['id'],'group':case['group'],'length':length,
                     'record':record,'judgement':judgement,
                     'expected_range_for_review':case['expected_range_for_review']}
                rows.append(row); emit(row)
    return rows
