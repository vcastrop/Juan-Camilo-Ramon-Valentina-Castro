"""Package the evaluated OCR path; no upload, inference or paid calls."""
import argparse
import json
from pathlib import Path
import subprocess
import zipfile

from final.build_space_candidate import ROOT,local_modules,digest,LICENSE_SHA
from final.config import MODELS


def render_app(template,bootstrap,payload_sha,commit):
    replacements={
        'from final.service_contract import Service, InputError, validate, event':
        'from final.service_contract import InputError, validate, event\nfrom final.service_ocr import OCRService as Service',
        'from final.service_runtime import load_runtime':'from final.integration_ocr20 import load_runtime',
        'El candidato FP16 conserva seis fallos de dominio en 22 entradas evaluadas.':
        'Perfil OCR: 18/22 casos de dominio en la evaluación de referencia; cuatro fallos textuales. No certifica este servidor.',
    }
    for old,new in replacements.items():
        if template.count(old)!=1:raise ValueError('Historical template changed; review explicit OCR adaptation')
        template=template.replace(old,new)
    return template.replace('# __BOOTSTRAP__',bootstrap).replace('__PAYLOAD_SHA__',payload_sha).replace('__SOURCE_COMMIT__',commit)


def build(output,license_file):
    from final.service_runtime import verify_assets
    verify_assets()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    names=local_modules(['final/integration_ocr20.py','final/service_ocr.py','final/service_telemetry.py'])
    templates=['final/space_candidate/app.py','final/space_candidate/requirements.txt','final/space_payload.py',
               'final/space_ocr/README.md','final/space_ocr/packages.txt','final/build_space_ocr.py']
    for name in names+templates:
        saved=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
        if saved.replace(b'\r\n',b'\n')!=(ROOT/name).read_bytes().replace(b'\r\n',b'\n'):
            raise ValueError('Commit source differs: '+name)
    license_data=Path(license_file).read_bytes()
    if digest(license_data)!=LICENSE_SHA:raise ValueError('Official Qwen license hash differs')
    files={n:(ROOT/n).read_bytes().replace(b'\r\n',b'\n') for n in names}
    for name in ['m3/corpus/documents.jsonl','model/contractrisk_robertalex_lora_adapter.zip']:
        files[name]=(ROOT/name).read_bytes()
    files['licenses/QWEN_RESEARCH_LICENSE.txt']=license_data
    files['NOTICE.txt']=b'Built with Qwen. Qwen RESEARCH LICENSE AGREEMENT, Copyright (c) Alibaba Cloud. All Rights Reserved. Academic research/evaluation only.\n'
    manifest={'source_commit':commit,'profile':'integrated_ocr20_fp16','precision':'fp16',
              'models':{k:v for k,v in MODELS.items() if k!='vision'},'visual_reader':'tesseract_cpu',
              'files':{n:digest(b) for n,b in files.items()},
              'scope':'inference only; no gold, judge, saved answers or API keys'}
    files['manifest.json']=json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2).encode()
    output=Path(output)
    if output.exists():raise ValueError('Use a new output directory')
    output.mkdir(parents=True)
    archive=output/'runtime_payload.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,raw in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;z.writestr(info,raw)
    app=render_app((ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8'),
                   (ROOT/'final/space_payload.py').read_text(encoding='utf-8'),digest(archive.read_bytes()),commit)
    compile(app,'generated_app.py','exec')
    (output/'app.py').write_text(app,encoding='utf-8',newline='\n')
    for name,source in [('README.md','final/space_ocr/README.md'),('packages.txt','final/space_ocr/packages.txt'),
                        ('requirements.txt','final/space_candidate/requirements.txt')]:
        (output/name).write_bytes((ROOT/source).read_bytes().replace(b'\r\n',b'\n'))
    return {'source_commit':commit,'payload_sha256':digest(archive.read_bytes()),'profile':manifest['profile'],
            'payload_files':sorted(files),'upload_files':sorted(p.name for p in output.iterdir()),
            'inference_tested_locally':False,'public_deployment_verified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--license-file',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.output,a.license_file),indent=2))
