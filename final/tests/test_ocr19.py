import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'m3')]
from final.ocr_candidate19 import parse_tsv, consensus, SETTINGS
from final.ocr_probe19 import load_protocol, diagnose


def tsv(lines,conf=95):
    header='level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tconf\ttext\n'
    return header+''.join(f'5\t1\t1\t1\t{i}\t{j}\t{conf}\t{word}\n' for i,line in enumerate(lines,1) for j,word in enumerate(line.split(),1))


class OCR19Tests(unittest.TestCase):
    def observations(self,amount='250000000',conf=95):
        parsed,evidence,confidence=parse_tsv(tsv(['Identificador del contrato: CO1.PCCNTR.1088236',
            'Modalidad de contratación: Mínima cuantía','Valor del contrato (COP): '+amount],conf))
        return {'parsed':parsed,'evidence':evidence,'confidence':confidence}

    def test_exact_agreement_preserves_digits(self):
        a=self.observations()
        self.assertEqual(consensus([a,copy.deepcopy(a)])['valor_cop'],'250000000')

    def test_extra_zero_disagreement_never_repaired(self):
        with self.assertRaises(ValueError):consensus([self.observations(),self.observations('2500000000')])

    def test_low_confidence_rejected(self):
        a=self.observations(conf=79)
        with self.assertRaises(ValueError):consensus([a,a])

    def test_duplicate_amount_rejected(self):
        parsed,evidence,confidence=parse_tsv(tsv(['Identificador del contrato: CO1.PCCNTR.1088236',
            'Modalidad: Mínima cuantía','Valor del contrato (COP): 250000000','Valor del contrato (COP): 2500000000']))
        a={'parsed':parsed,'evidence':evidence,'confidence':confidence}
        with self.assertRaises(ValueError):consensus([a,a])

    def test_grouped_literal_supported_not_invented(self):
        a=self.observations('250.000.000 COP')
        self.assertEqual(consensus([a,a])['valor_cop'],'250000000')

    def test_missing_id_no_guessing(self):
        a=self.observations();a['parsed']['id_contrato']=None
        with self.assertRaises(ValueError):consensus([a,a])

    def test_nonfinite_confidence_rejected(self):
        with self.assertRaises(ValueError):self.observations(conf='nan')
        with self.assertRaises(ValueError):parse_tsv('level\tconf\ttext\n')

    def test_frozen_twelve_cases_and_no_corpus(self):
        p=load_protocol()
        self.assertEqual(len(p['cases']),12)
        self.assertEqual(sum(c['complete'] for c in p['cases']),8)
        self.assertFalse(p['corpus_used_in_reading'])
        self.assertEqual(SETTINGS['psm'],[3,6])

    def test_ocr_success_does_not_mean_source_agreement(self):
        case=next(c for c in load_protocol()['cases'] if c['id']=='altered_amount')
        d=diagnose(case,{'output':dict(case['expected'],legible=True),'parse_error':None})
        self.assertTrue(d['complete_read_automatic_only'])
        self.assertFalse(d['qa_answer_validated'])
        self.assertEqual(d['observed_route'],'needs_source_and_answer_validation')


if __name__=='__main__':unittest.main()
