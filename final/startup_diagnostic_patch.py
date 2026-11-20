"""Add bounded technical diagnostics to the published app, not to inference."""
import json
from pathlib import Path
import re
import traceback

VERSION='ocr22-startup-diagnostic-1'


def startup_diagnostic(error):
    # Never serialize str(error), args, source lines, locals, URLs or full paths.
    message=str(error).lower()
    known={
        'cannot copy out of meta tensor':'meta_tensor_materialization',
        'size mismatch':'adapter_tensor_size_mismatch',
        'unexpected keyword argument':'python_api_argument_mismatch',
        'out of memory':'memory_exhausted',
        'no kernel image':'gpu_architecture_mismatch',
        'torchvision::nms':'torchvision_operator_missing',
        'no module named':'missing_python_module',
        'software_environment_not_ready':'software_environment_not_ready',
        'not compiled with cuda':'torch_without_cuda',
        'no nvidia driver':'cuda_driver_not_available',
        'could not find cuda':'cuda_not_available',
        'safetensor':'safetensors_loading_error',
        'state_dict':'state_dict_loading_error',
    }
    code=next((code for fragment,code in known.items() if fragment in message),'unclassified_startup_exception')
    frames=[]
    for frame in traceback.extract_tb(error.__traceback__)[-10:]:
        name=Path(frame.filename).name
        frames.append({'module_file':name if re.fullmatch(r'[A-Za-z0-9_.-]{1,90}',name) else 'redacted',
                       'line':frame.lineno,'function':frame.name if re.fullmatch(r'[A-Za-z0-9_<>]{1,90}',frame.name) else 'redacted'})
    data={'event':'contractrisk_startup_diagnostic','diagnostic_version':VERSION,
          'error_type':type(error).__name__,'reason_code':code,'frames':frames,
          'exception_message_retained':False,'private_values_retained':False}
    if isinstance(error,ModuleNotFoundError):
        module=getattr(error,'name',None)
        if isinstance(module,str) and re.fullmatch(r'[A-Za-z0-9_.]{1,90}',module):data['missing_module']=module
    return data


def patch_app(app):
    old="except Exception:\n    # No private paths, provider exception bodies or tokens in logs/UI.\n    print('ContractRisk startup_failed: models_or_index_not_ready', flush=True)"
    new="except Exception as startup_exc:\n    print(json.dumps(startup_diagnostic(startup_exc)), flush=True)\n    print('ContractRisk startup_failed: models_or_index_not_ready', flush=True)"
    if app.count(old)!=1:raise ValueError('Unexpected original startup handler')
    module_source=Path(__file__).read_text(encoding='utf-8')
    # Include just the diagnostic definition and its standard-library imports.
    diagnostic=module_source.split('def startup_diagnostic(error):',1)[1].split('\n\ndef patch_app',1)[0]
    injected='import json\nimport re\nimport traceback\n'+f'VERSION={VERSION!r}\n'+'def startup_diagnostic(error):'+diagnostic+'\n'
    anchor='from fastapi.responses import JSONResponse'
    if app.count(anchor)!=1:raise ValueError('Unexpected app import boundary')
    result=app.replace(anchor,injected+'\n'+anchor).replace(old,new)
    compile(result,'app.py','exec')
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('app',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=patch_app(args.app.read_text(encoding='utf-8'))
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(result)
