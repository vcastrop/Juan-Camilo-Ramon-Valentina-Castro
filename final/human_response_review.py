"""Read declared human annotations; retain doubts and never create LLM grades."""
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS=['Respuesta respaldada','Explicación respaldada y no vacía','Completa para lo preguntado',
        'Citas respaldan lo afirmado','Abstención adecuada','Fallos críticos']


def parse(text,manifest,protocol):
    expected={entry['review_key'] for entry in manifest};rows={}
    reviewer=re.search(r'^Revisor/a: (.+)$',text,re.M);date=re.search(r'^Fecha real: (\d{4}-\d{2}-\d{2})$',text,re.M)
    if not reviewer or reviewer[1].strip()=='PENDIENTE' or not date:raise ValueError('Missing declared reviewer/date')
    for section in re.split(r'^## ',text,flags=re.M)[1:]:
        key=section.splitlines()[0].strip()
        if key not in expected:
            if key.startswith('integrated_'):raise ValueError('Unknown case')
            continue
        if key in rows:raise ValueError('Duplicate case')
        values={}
        for field in FIELDS:
            hits=re.findall(r'^'+re.escape(field)+r': (.+)$',section,re.M)
            if len(hits)!=1:raise ValueError('Missing or repeated field: '+key+'/'+field)
            value=hits[0].strip()
            allowed=set(protocol['critical_failure_types'])|{'NINGUNO','DUDOSO'} if field=='Fallos críticos' else {'SI','NO','DUDOSO'}|({'NO_APLICA'} if field.startswith('Citas ') else set())
            if value not in allowed:raise ValueError('Unknown annotation: '+key+'/'+field)
            values[field]=value
        notes=re.search(r'^Observaciones: (.+)$',section,re.M)
        if not notes or notes[1].strip()=='PENDIENTE':raise ValueError('Missing observations')
        rows[key]={'criteria':values,'observations':notes[1].strip()}
    if set(rows)!=expected:raise ValueError('Review does not cover all 44 records')
    return {'reviewer_declared':reviewer[1].strip(),'date_declared':date[1],
            'status':'received_with_open_adjudications' if any('DUDOSO' in r['criteria'].values() for r in rows.values()) else 'received',
            'annotations':rows,'judge_grades_created':False}


def analyze(review,manifest):
    rows=review['annotations'];lookup={entry['review_key']:entry for entry in manifest}
    open_items={key:[f for f,v in row['criteria'].items() if v=='DUDOSO'] for key,row in rows.items() if 'DUDOSO' in row['criteria'].values()}
    new_critical=[]
    for key in rows:
        if not key.startswith('integrated_nf4/'):continue
        other=key.replace('integrated_nf4/','integrated_fp16/')
        left=rows[other]['criteria']['Fallos críticos'];right=rows[key]['criteria']['Fallos críticos']
        if left!='DUDOSO' and right not in {'DUDOSO','NINGUNO'} and right!=left:
            new_critical.append({'id':key.split('/')[1],'type':right,'reviewer':review['reviewer_declared']})
    regressions=[]
    def adequate(key):
        criteria=rows[key]['criteria']
        if 'NO' in criteria.values() or criteria['Fallos críticos'] not in {'NINGUNO','DUDOSO'}:return False
        if 'DUDOSO' in criteria.values():return None
        return True
    for base,variant in [('vis_01','vis_09_contrast'),('vis_02','vis_10_rotation')]:
        l=[adequate('integrated_fp16/'+cid) for cid in [base,variant]]
        r=[adequate('integrated_nf4/'+cid) for cid in [base,variant]]
        if all(value is True for value in l) and any(value is False for value in r):
            regressions.append({'control':'invariance','base':base,'variant':variant,
                                'reason':'FP16 both complete/supported; NF4 repeats the same omission. Equality alone is not correctness.'})
    return {'reviewer_declared':review['reviewer_declared'],'date_declared':review['date_declared'],
        'records_reviewed':len(rows),'records_with_doubts':len(open_items),'open_items':open_items,
        'new_confirmed_critical_failures_nf4':new_critical,'human_control_regressions':regressions,
        'nf4_deployment_veto':bool(new_critical or regressions),
        'decision_scope':'Human predeclared critical/control veto, not complete numerical efficiency acceptance.',
        'formal_efficiency_status':'not_evaluable_judge_and_remaining_semantic_adjudication_pending',
        'domain_rate':None,'judge_validated':False,'llm_grades_created':False,
        'denominator_erratum':'Reviewer summary says 6/8 unblocked visual requests omit amount; correct: 8 answerable, 1 blocked, 6/7 unblocked omit amount. Original review unchanged.'}


def load_received():
    original=ROOT/'final/evidence/human_response_review_01/original_review.md'
    manifest=json.loads((ROOT/'final/eval/review_comparison02/manifest.json').read_text(encoding='utf-8'))
    protocol=json.loads((ROOT/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
    result=parse(original.read_text(encoding='utf-8-sig'),manifest,protocol)
    result['source_review_sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
    return result,analyze(result,manifest)
