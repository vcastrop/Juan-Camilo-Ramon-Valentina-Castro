"""Read-only repository checks plus disposable deterministic reproductions (no GPU)."""
import argparse, csv, hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import unquote

p = argparse.ArgumentParser()
p.add_argument('root', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
root = a.root.resolve(); m3 = root/'m3'
a.output.mkdir(parents=True, exist_ok=False)
sys.path.insert(0, str(m3))
from harness_m3_v11 import rescore, scorecard
from run_final_m3 import load_gold
from ragas_m3_v11 import summarize, METRICS
from rescore_m3 import build

def jsonl(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
def csvrows(path):
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
def close(observed, expected):
    if expected is None: return observed == ''
    if isinstance(expected, (float, int)): return abs(float(observed)-expected)<1e-10
    return str(observed)==str(expected)

report = {'scope': 'clean GitHub checkout; CPU audit only; no model inference or GPU installation',
          'checks': {}, 'warnings': []}
proc = subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','m3/tests','-q'],
                      cwd=root, capture_output=True, text=True, encoding='utf-8')
(a.output/'tests.log').write_text(proc.stdout+proc.stderr,encoding='utf-8')
assert proc.returncode == 0, proc.stderr
report['checks']['tests'] = re.search(r'Ran (\d+) tests',proc.stderr).group(1)

docs = [root/'README.md'] + [m3/x for x in ['README.md','RUTA_ENTREGA.md','CHECKLIST.md',
        'CONTINUAR_TRABAJO.md','corpus/README.md','JUEZ_M3.md']]
broken=[]; links=0; external=set()
for doc in docs:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if target.startswith(('http:', 'https:')): external.add(target); continue
        if target.startswith('#'): continue
        path=unquote(target.split('#')[0]).strip('<>')
        if not path: continue
        links+=1
        if not (doc.parent/path).exists(): broken.append([str(doc.relative_to(root)),target])
report['checks']['local_links']={'checked':links,'broken':broken,'external_not_http_checked':sorted(external)}

gold=load_gold(); byid={c['eval_id']:c for c in gold}
items=jsonl(m3/'results/final_m3/harness_rows.jsonl')
assert len(items)==72 and len({(i['row']['variant'],i['row']['eval_id']) for i in items})==72
for i in items: assert i['record']['question']==byid[i['row']['eval_id']]['input']
report['checks']['gold']={'cases':len(gold),'unanswerable':sum(c['kind']=='unanswerable' for c in gold),
                        'responses':len(items),'reference_leak_check':'system called with question only; source inspected'}
rows=[rescore(byid[i['row']['eval_id']],i) for i in items]
cards={v:scorecard([r for r in rows if r['variant']==v]) for v in {r['variant'] for r in rows}}
for saved in csvrows(m3/'results/final_m3_rescore_v1_1/scorecard_m3_v1_1.csv'):
    for k,v in cards[saved['variant']].items():
        if k in saved: assert close(saved[k],v),(saved['variant'],k,saved[k],v)
out=a.output/'rescore_reproduction'
build(m3/'results/final_m3',out)
for name in ['scorecard_m3_v1_1.csv','scorecard_casos_m3_v1_1.csv','tablas_m3_v1_1.md']:
    assert (out/name).read_text(encoding='utf-8')==(m3/'results/final_m3_rescore_v1_1'/name).read_text(encoding='utf-8'),name
report['checks']['rescore']='all 72 rows and exported tables reproduced; normalized line endings'

rag=jsonl(m3/'results/final_m3_ragas_v1_1/ragas_v1_1.jsonl')
sums={v:summarize([r for r in rag if r['variant']==v]) for v in {r['variant'] for r in rag}}
for saved in csvrows(m3/'results/final_m3_ragas_v1_1/ragas_m3_v1_1.csv'):
    for k,v in sums[saved['variant']].items(): assert close(saved[k],v),(k,saved[k],v)
report['checks']['ragas']={'cases':len(rag),'calls':sum(len(r['judge_calls']) for r in rag),
                         'parse_failures':sum(r['judge_parse_failures'] for r in rag), 'aggregates_match':True}

# Check the exact rounded values printed in the two main README score tables.
text=(m3/'README.md').read_text(encoding='utf-8')
def table_after(marker):
    section=text.split(marker,1)[1]
    return [re.sub(r'\*','',s).strip() for s in section.splitlines() if s.startswith('|')][2:]
evolution=table_after('### Tabla evolutiva')[:6]
variants=['sin_rag','rag_ingenuo','rag_avanzado','sistema_final','ablacion_solo_hibrido','ablacion_denso_rerank']
for line,v in zip(evolution,variants):
    parts=[x.strip() for x in line.strip('|').split('|')]; c=cards[v]
    for idx,key,d in [(1,'dim1_fact_coverage',3),(3,'dim2_judge_mean',2),(5,'latency_median_seconds',2)]:
        assert parts[idx]==f'{c[key]:.{d}f}'.replace('.',','),(v,key,parts[idx])
    assert parts[2]==f"{c['dim1_complete_answers']}/12"
    assert parts[4].split('→')[-1].strip()==f"{c['dim3_domain_passed']}/12"
for line,v in zip(table_after('### RAGAS 1.1')[:3],['rag_ingenuo','rag_avanzado','sistema_final']):
    parts=[x.strip() for x in line.strip('|').split('|')]
    for cell,key in zip(parts[1:],METRICS):
        assert cell==f"{sums[v][key]:.3f} (n={sums[v][key+'_n']})".replace('.',','),(v,key,cell)
report['checks']['readme_tables']='6 harness rows and 3 RAGAS 1.1 rows match detail-derived values and denominators'

nb_checks=[]
for name in ['ContractRisk_M3_Final_Colab.ipynb','ContractRisk_M3_RAGAS_v1_1_Colab.ipynb']:
    nb=json.loads((m3/name).read_text(encoding='utf-8'))
    for i,c in enumerate(nb['cells']):
        if c['cell_type']=='code': compile(''.join(c['source']),name+str(i),'exec')
    nb_checks.append(name)
report['checks']['notebook_syntax']=nb_checks

# Detect high-specificity credential shapes without printing any values.
patterns={'github_token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})',
          'hf_token':r'\bhf_[A-Za-z0-9]{30,}', 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'}
secrets=[]; scanned=0; local_paths=[]
for f in [root/'README.md']+list(m3.rglob('*')):
    if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts:continue
    if f.suffix not in ['.py','.md','.json','.jsonl','.ipynb','.txt','.csv','.log']:continue
    content=f.read_text(encoding='utf-8',errors='replace'); scanned+=1
    for kind,pattern in patterns.items():
        if re.search(pattern,content): secrets.append({'file':str(f.relative_to(root)),'kind':kind})
    if f.parent==m3 and f.suffix in ['.py','.md'] and re.search(r'[A-Za-z]:[\\/](?:Users|home)[\\/]',content):
        local_paths.append(str(f.relative_to(root)))
report['checks']['credential_pattern_scan']={'files':scanned,'matches':secrets,'scope':'M3 and root README, not complete Git history or binary ZIPs'}
report['checks']['machine_specific_entry_paths']=local_paths
report['checks']['models_and_licenses']='reviewed declarations, pinned model revisions and corpus source attribution; not legal certification'
report['warnings']=['No fresh GPU inference or pip installation performed locally.',
                    'Human contribution and corpus privacy review cannot be invented.',
                    'Known abstention and judge failures remain; tests do not prove semantic quality.']
(a.output/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
