"""Prepare fixed synthetic CPU OCR pilot inputs before its first real run."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
from final.ocr_candidate19 import SETTINGS


def prepare(font_path):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    folder=ROOT/'final/evidence/ocr19_protocol'
    if folder.exists():raise ValueError('Do not replace a frozen protocol')
    folder.mkdir(parents=True)
    old=json.loads((ROOT/'final/evidence/visual18_protocol/protocol.json').read_text(encoding='utf-8'))
    cases=[]
    for c in old['cases']:
        name='final/evidence/visual18_protocol/'+c['file']
        expectation=c['expected_for_diagnostics_only']
        route='unreadable' if c['id']=='blank' else 'missing_visual_fields' if c['id']=='missing_amount' else 'needs_source_and_answer_validation'
        cases.append({'id':c['id'],'file':name,'sha256':c['image_sha256'],'expected':expectation,
            'expected_route':route,'complete':route=='needs_source_and_answer_validation',
            'source':'same frozen pixels from failed Qwen18; altered amount means reading test only, not verified source truth'})
    font=ImageFont.truetype(str(font_path),30)
    for identity, amount, has_id, duplicate in [
        ('new_fictional_plain','15387424',True,False),
        ('new_fictional_grouped','15.387.424 COP',True,False),
        ('missing_id','12345',False,False),
        ('ambiguous_amount','75000000',True,True)]:
        lines=['FICHA SINTETICA DE PRUEBA. NO ES DOCUMENTO FIRMADO.']
        if has_id:lines.append('Identificador del contrato: CO1.PCCNTR.999000111')
        lines+=['Objeto registrado: Mantenimiento preventivo de equipos durante doce meses.',
                'Modalidad de contratación: Contratación directa','Valor del contrato (COP): '+amount]
        if duplicate:lines.append('Valor del contrato (COP): 750000000')
        text='\n\n'.join(textwrap.fill(s,width=60) for s in lines)
        image=Image.new('RGB',(1200,70+len(text.splitlines())*44),'white')
        ImageDraw.Draw(image).multiline_text((25,20),text,font=font,fill='black',spacing=10)
        path=folder/(identity+'.png');image.save(path)
        complete=has_id and not duplicate
        expected={'id_contrato':'CO1.PCCNTR.999000111','modalidad':'Contratación directa','valor_cop':'15387424'} if complete else None
        cases.append({'id':identity,'file':path.relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'expected':expected,
            'expected_route':'needs_source_and_answer_validation' if complete else 'visual_schema',
            'complete':complete,'source':'new fictional fixture; no corpus or final evaluation example'})
    protocol={'version':'ocr-only-pilot-19','post_hoc':True,'settings':SETTINGS,'cases':cases,
              'corpus_used_in_reading':False,'qa_or_public_service_tested':False,
              'font_sha256':hashlib.sha256(Path(font_path).read_bytes()).hexdigest(),
              'interpretation':'8 complete reading cases + missing-value partial, blank, missing-ID and ambiguous-value controls. Two layouts share an engine; confidence is not probability of correctness.'}
    (folder/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    return protocol


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--font',type=Path,required=True)
    print(json.dumps(prepare(p.parse_args().font),ensure_ascii=False,indent=2))
