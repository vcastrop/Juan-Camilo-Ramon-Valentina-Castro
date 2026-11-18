"""Same acceptance thresholds, plus independently recomputed support checks."""
import copy
from final.reasoning_calibration import validate_config as validate_previous,pilot_summary as previous_pilot,full_summary as previous_full
from final.calibration_final import cases
from final.judge_literal import support_issues,parse_literal

PILOT_IDS=['short_good','short_bad','number_bad','conflict_good','conflict_bad',
           'empty_explanation_bad','citation_bad','attribution_bad','accusation_good']


def validate_config(config):
    old=copy.deepcopy(config)
    if config.get('protocol')!='literal-support-reasoning-judge-1' or config.get('pilot_ids')!=PILOT_IDS:
        raise ValueError('Unexpected literal-support protocol')
    if config.get('normalization')!='exact_whole_block_repetition_only_mitigated':raise ValueError('Unexpected normalization')
    old['pilot_ids']=PILOT_IDS[:7];validate_previous(old)


def checked_rows(rows):
    result=copy.deepcopy(rows);anchors={c['id']:c['record'] for c in cases()}
    for r in result:
        j=r['judgement'];issues=list(j.get('internal_inconsistencies',[]))
        try:
            obj={'verificaciones':j.get('checks'),'soportes':j.get('supports'),'puntaje':j.get('score'),'razon':j.get('reason')}
            import json
            parse_literal(json.dumps(obj))
            issues+=support_issues(obj,anchors[r['id']])
        except (ValueError,TypeError):issues.append('invalid_or_missing_literal_support')
        j['internal_inconsistencies']=sorted(set(issues))
    return result


def pilot_summary(rows,ids):return previous_pilot(checked_rows(rows),ids)
def full_summary(rows):return previous_full(checked_rows(rows))
