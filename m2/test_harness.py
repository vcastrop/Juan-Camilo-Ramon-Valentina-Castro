"""Pruebas pequeñas del núcleo; no descargan modelos."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from harness import HarnessConfig, classification_metrics, harness, parse_judge_response


class FakeSystem:
    def predict_many(self, texts):
        return [
            {"label": "REQUIERE_REVISION", "confidence": 0.8},
            {"label": "REQUIERE_REVISION", "confidence": 0.7},
        ]


class FakeJudge:
    def evaluate(self, example, prediction):
        return {
            "score": 4 if example["expected"] == prediction["label"] else 1,
            "reason": "Resultado controlado.",
            "parse_ok": True,
        }


EXAMPLES = [
    {
        "eval_id": "a",
        "id_contrato": "1",
        "descripcion_del_proceso": "Apoyo a la gestión.",
        "tipo_de_contrato": "Servicios",
        "expected": "REQUIERE_REVISION",
        "criterio_gold": "No concreta la actividad.",
        "caso_frontera": "SI",
    },
    {
        "eval_id": "b",
        "id_contrato": "2",
        "descripcion_del_proceso": "Comprar diez computadores portátiles.",
        "tipo_de_contrato": "Suministros",
        "expected": "SUFICIENTE",
        "criterio_gold": "Identifica el bien.",
        "caso_frontera": "NO",
    },
]


class HarnessTests(unittest.TestCase):
    def test_classification_metrics(self):
        metrics = classification_metrics(
            ["REQUIERE_REVISION", "SUFICIENTE"],
            ["REQUIERE_REVISION", "REQUIERE_REVISION"],
        )
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertEqual(metrics["confusion_matrix"], [[1, 0], [1, 0]])
        self.assertAlmostEqual(metrics["macro_f1"], 1 / 3)

    def test_judge_parser(self):
        result = parse_judge_response('```json\n{"score": 4, "reason": "Correcto"}\n```')
        self.assertEqual(result["score"], 4)
        self.assertTrue(result["parse_ok"])

    def test_end_to_end_with_controlled_components(self):
        with tempfile.TemporaryDirectory() as directory:
            result = harness(
                EXAMPLES,
                FakeSystem(),
                FakeJudge(),
                directory,
                HarnessConfig(seed=42),
            )
            self.assertEqual(result["metrics"]["macro_f1"], 1 / 3)
            self.assertEqual(result["metrics"]["contract_review_utility"], 0.75)
            self.assertEqual(result["metrics"]["judge_mean_1_5"], 2.5)
            self.assertTrue((Path(directory) / "scorecard_baseline.csv").exists())
            self.assertTrue((Path(directory) / "predictions_baseline.csv").exists())
            metrics = json.loads((Path(directory) / "metrics_baseline.json").read_text())
            self.assertEqual(metrics["frontier_count"], 1)
            with (Path(directory) / "scorecard_baseline.csv").open(encoding="utf-8-sig") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 3)


if __name__ == "__main__":
    unittest.main()
