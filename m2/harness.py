"""Harness reutilizable de evaluación para ContractRisk.

El núcleo no depende de un modelo concreto. Cualquier sistema que implemente
``predict_many(texts)`` y devuelva label/confidence/explanation puede evaluarse.
"""

from __future__ import annotations

import csv
import json
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

import numpy as np


ALLOWED_LABELS = ("REQUIERE_REVISION", "SUFICIENTE")


class BatchSystem(Protocol):
    def predict_many(self, texts: list[str]) -> list[dict[str, Any]]:
        """Devuelve una predicción normalizada por texto y conserva el orden."""


class Judge(Protocol):
    def evaluate(self, example: dict[str, str], prediction: dict[str, Any]) -> dict[str, Any]:
        """Devuelve score entero 1-5, reason y parse_ok."""


@dataclass(frozen=True)
class HarnessConfig:
    seed: int = 42
    judge_pass_threshold: int = 4
    explanation_word_limit: int = 80


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def load_eval_set(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "eval_id",
        "id_contrato",
        "descripcion_del_proceso",
        "expected",
        "criterio_gold",
        "caso_frontera",
    }
    if not rows:
        raise ValueError("El eval set está vacío.")
    missing_columns = required - set(rows[0])
    if missing_columns:
        raise ValueError(f"Faltan columnas: {sorted(missing_columns)}")
    if len({row["eval_id"] for row in rows}) != len(rows):
        raise ValueError("eval_id debe ser único.")
    for row in rows:
        if row["expected"] not in ALLOWED_LABELS:
            raise ValueError(f"Etiqueta gold inválida en {row['eval_id']}: {row['expected']}")
        if row["caso_frontera"] not in {"SI", "NO"}:
            raise ValueError(f"caso_frontera inválido en {row['eval_id']}")
        if not row["descripcion_del_proceso"].strip() or not row["criterio_gold"].strip():
            raise ValueError(f"Texto o criterio vacío en {row['eval_id']}")
    return rows


def normalize_prediction(raw: Any, word_limit: int = 80) -> dict[str, Any]:
    if isinstance(raw, str):
        raw = {"label": raw}
    if not isinstance(raw, dict):
        raise TypeError("Cada predicción debe ser str o dict.")

    label = str(raw.get("label", "")).strip().upper()
    if label not in ALLOWED_LABELS:
        raise ValueError(f"Etiqueta predicha inválida: {label!r}")

    confidence = raw.get("confidence")
    if confidence is not None:
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence debe estar entre 0 y 1.")

    explanation = str(raw.get("explanation") or "").strip()
    explanation = " ".join(explanation.split()[:word_limit])
    return {"label": label, "confidence": confidence, "explanation": explanation}


def contract_review_utility(expected: str, predicted: str) -> float:
    if expected == predicted:
        return 1.0
    if expected == "SUFICIENTE" and predicted == "REQUIERE_REVISION":
        return 0.5
    return 0.0


def safe_mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return float(np.mean(values)) if values else None


def classification_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    """Calcula métricas binarias sin depender de estado externo."""

    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("Las listas de etiquetas deben tener igual longitud y no estar vacías.")
    per_class: dict[str, dict[str, float | int]] = {}
    matrix: list[list[int]] = []
    for real_label in ALLOWED_LABELS:
        matrix.append(
            [
                sum(real == real_label and pred == predicted_label for real, pred in zip(y_true, y_pred))
                for predicted_label in ALLOWED_LABELS
            ]
        )
    for label in ALLOWED_LABELS:
        tp = sum(real == label and pred == label for real, pred in zip(y_true, y_pred))
        fp = sum(real != label and pred == label for real, pred in zip(y_true, y_pred))
        fn = sum(real == label and pred != label for real, pred in zip(y_true, y_pred))
        support = sum(real == label for real in y_true)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    return {
        "accuracy": sum(real == pred for real, pred in zip(y_true, y_pred)) / len(y_true),
        "macro_f1": safe_mean(per_class[label]["f1"] for label in ALLOWED_LABELS),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def harness(
    eval_set: str | Path | list[dict[str, str]],
    system: BatchSystem,
    judge: Judge | None,
    output_dir: str | Path,
    config: HarnessConfig | None = None,
) -> dict[str, Any]:
    """Ejecuta las tres dimensiones y escribe un scorecard reproducible."""

    config = config or HarnessConfig()
    set_seed(config.seed)
    examples = load_eval_set(eval_set) if isinstance(eval_set, (str, Path)) else eval_set
    texts = [row["descripcion_del_proceso"] for row in examples]
    raw_predictions = system.predict_many(texts)
    if len(raw_predictions) != len(examples):
        raise ValueError("El sistema no devolvió una predicción por ejemplo.")
    predictions = [
        normalize_prediction(raw, config.explanation_word_limit) for raw in raw_predictions
    ]

    detail_rows: list[dict[str, Any]] = []
    for example, prediction in zip(examples, predictions):
        judge_result = (
            judge.evaluate(example, prediction)
            if judge is not None
            else {"score": None, "reason": "Juez no ejecutado", "parse_ok": False}
        )
        score = judge_result.get("score")
        if score is not None and int(score) not in range(1, 6):
            raise ValueError(f"Puntaje del juez fuera de rango en {example['eval_id']}: {score}")
        utility = contract_review_utility(example["expected"], prediction["label"])
        detail_rows.append(
            {
                **example,
                "predicted": prediction["label"],
                "confidence": prediction["confidence"],
                "explanation": prediction["explanation"],
                "correct": example["expected"] == prediction["label"],
                "judge_score": score,
                "judge_reason": judge_result.get("reason", ""),
                "judge_parse_ok": bool(judge_result.get("parse_ok", False)),
                "judge_raw_score": judge_result.get("raw_score", score),
                "judge_guardrail_applied": bool(
                    judge_result.get("rubric_guardrail_applied", False)
                ),
                "judge_raw_response": judge_result.get("raw_response", ""),
                "domain_pass": bool(
                    example["expected"] == prediction["label"]
                    and score is not None
                    and int(score) >= config.judge_pass_threshold
                ),
                "domain_utility": utility,
            }
        )

    y_true = [row["expected"] for row in detail_rows]
    y_pred = [row["predicted"] for row in detail_rows]
    classic = classification_metrics(y_true, y_pred)
    judge_scores = [float(row["judge_score"]) for row in detail_rows if row["judge_score"] is not None]
    raw_correct_scores = [
        float(row["judge_raw_score"])
        for row in detail_rows
        if row["correct"] and row["judge_raw_score"] is not None
    ]
    raw_error_scores = [
        float(row["judge_raw_score"])
        for row in detail_rows
        if not row["correct"] and row["judge_raw_score"] is not None
    ]
    frontier_rows = [row for row in detail_rows if row["caso_frontera"] == "SI"]
    regular_rows = [row for row in detail_rows if row["caso_frontera"] == "NO"]

    metrics = {
        "total_examples": len(detail_rows),
        "seed": config.seed,
        "accuracy": classic["accuracy"],
        "macro_f1": classic["macro_f1"],
        "recall_requiere_revision": classic["per_class"]["REQUIERE_REVISION"]["recall"],
        "precision_requiere_revision": classic["per_class"]["REQUIERE_REVISION"]["precision"],
        "f1_requiere_revision": classic["per_class"]["REQUIERE_REVISION"]["f1"],
        "judge_mean_1_5": safe_mean(judge_scores),
        "judge_pass_rate": safe_mean(
            score >= config.judge_pass_threshold for score in judge_scores
        ),
        "judge_parse_success_rate": safe_mean(
            row["judge_parse_ok"] for row in detail_rows if row["judge_score"] is not None
        ),
        "judge_guardrail_rate": safe_mean(
            row["judge_guardrail_applied"] for row in detail_rows
        ),
        "judge_raw_mean_correct": safe_mean(raw_correct_scores),
        "judge_raw_mean_incorrect": safe_mean(raw_error_scores),
        "domain_compliance_rate": safe_mean(row["domain_pass"] for row in detail_rows),
        "contract_review_utility": safe_mean(row["domain_utility"] for row in detail_rows),
        "frontier_domain_compliance_rate": safe_mean(
            row["domain_pass"] for row in frontier_rows
        ),
        "frontier_accuracy": safe_mean(row["correct"] for row in frontier_rows),
        "regular_accuracy": safe_mean(row["correct"] for row in regular_rows),
        "frontier_count": len(frontier_rows),
        "confusion_labels": list(ALLOWED_LABELS),
        "confusion_matrix": classic["confusion_matrix"],
    }

    scorecard_rows = [
        {
            "dimension": "Métrica clásica automática",
            "metric": "macro_f1",
            "score": metrics["macro_f1"],
            "scale": "0-1; mayor es mejor",
        },
        {
            "dimension": "LLM-as-a-judge",
            "metric": "judge_mean_1_5",
            "score": metrics["judge_mean_1_5"],
            "scale": "1-5; mayor es mejor",
        },
        {
            "dimension": "Cumplimiento del dominio",
            "metric": "domain_compliance_rate",
            "score": metrics["domain_compliance_rate"],
            "scale": "0-1; etiqueta correcta y juez >= 4",
        },
    ]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "predictions_baseline.csv", detail_rows)
    _write_csv(output_dir / "scorecard_baseline.csv", scorecard_rows)
    with (output_dir / "metrics_baseline.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    return {"metrics": metrics, "scorecard": scorecard_rows, "details": detail_rows}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No hay filas para escribir en {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_judge_response(text: str) -> dict[str, Any]:
    """Analiza JSON estricto y usa una extracción acotada como respaldo."""

    cleaned = "\n".join(line.rstrip() for line in text.strip().splitlines())
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    candidates = [fenced.group(1)] if fenced else []
    object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if object_match:
        candidates.append(object_match.group(0))
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            score = int(data["score"])
            if score in range(1, 6):
                return {
                    "score": score,
                    "reason": str(data.get("reason", "")),
                    "parse_ok": True,
                    "raw_response": cleaned,
                }
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue

    score_match = re.search(r"(?:score|puntaje)\s*[:=]\s*([1-5])\b", cleaned, flags=re.I)
    if score_match:
        reason_match = re.search(r"(?:reason|raz[oó]n)\s*[:=]\s*(.+)", cleaned, flags=re.I | re.DOTALL)
        return {
            "score": int(score_match.group(1)),
            "reason": (reason_match.group(1).strip() if reason_match else cleaned)[:500],
            "parse_ok": True,
            "raw_response": cleaned,
        }
    raise ValueError(f"No se pudo extraer un puntaje 1-5 del juez: {cleaned[:200]!r}")


class TransformersRubricJudge:
    def __init__(
        self,
        rubric_path: str | Path,
        model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
        device: str | None = None,
        seed: int = 42,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.rubric = json.loads(Path(rubric_path).read_text(encoding="utf-8"))
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()
        set_seed(seed)

    def evaluate(self, example: dict[str, str], prediction: dict[str, Any]) -> dict[str, Any]:
        levels = "\n".join(
            f"{level}: {description}" for level, description in self.rubric["levels"].items()
        )
        labels_match = prediction["label"] == example["expected"]
        allowed_scores = "3, 4 o 5" if labels_match else "1 o 2"
        prompt = f"""Eres un juez de calidad para clasificación contractual.
La etiqueta esperada es {example['expected']}.
La etiqueta del sistema es {prediction['label']}.
¿Coinciden exactamente?: {'SI' if labels_match else 'NO'}.
REGLA OBLIGATORIA: el puntaje solo puede ser {allowed_scores}.
Evalúa después la explicación. No premies longitud ni estilo. No infieras fraude o ilegalidad.

RÚBRICA:
{levels}

CASO:
Texto: {example['descripcion_del_proceso']}
Etiqueta esperada: {example['expected']}
Criterio gold: {example['criterio_gold']}
Caso frontera: {example['caso_frontera']}

SALIDA DEL SISTEMA:
Etiqueta: {prediction['label']}
Confianza: {prediction.get('confidence')}
Explicación: {prediction.get('explanation') or '[sin explicación]'}

No copies frases de estas instrucciones. Responde exactamente en dos líneas.
La primera empieza con PUNTAJE= y contiene un nivel permitido.
La segunda empieza con RAZON= y contiene una justificación de máximo 40 palabras.
"""
        messages = [
            {
                "role": "system",
                "content": (
                    "Sigue la rúbrica literalmente y responde únicamente en las dos "
                    "líneas solicitadas: PUNTAJE= y RAZON=."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        first_response = self._generate(messages)
        try:
            return apply_rubric_guardrail(
                example, prediction, parse_judge_response(first_response)
            )
        except ValueError:
            repair_messages = messages + [
                {"role": "assistant", "content": first_response},
                {
                    "role": "user",
                    "content": "Reescribe el veredicto en dos líneas: PUNTAJE= con un nivel permitido y RAZON= con una justificación breve. No copies esta instrucción.",
                },
            ]
            second_response = self._generate(repair_messages)
            try:
                return apply_rubric_guardrail(
                    example, prediction, parse_judge_response(second_response)
                )
            except ValueError:
                return {
                    "score": None,
                    "reason": "Dos respuestas no analizables del juez; el caso queda sin puntaje.",
                    "parse_ok": False,
                    "raw_score": None,
                    "rubric_guardrail_applied": False,
                    "raw_response": second_response,
                }

    def _generate(self, messages: list[dict[str, str]]) -> str:
        formatted = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(formatted, return_tensors="pt").to(self.device)
        output = self.model.generate(
            **inputs,
            max_new_tokens=96,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        generated = output[0, inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(generated, skip_special_tokens=True)


def apply_rubric_guardrail(
    example: dict[str, str], prediction: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    """Impide niveles incompatibles con las anclas objetivas de la rúbrica."""

    raw_score = int(result["score"])
    labels_match = prediction["label"] == example["expected"]
    has_explanation = bool(str(prediction.get("explanation") or "").strip())
    if labels_match and not has_explanation:
        score = 4
    elif not labels_match and not has_explanation:
        score = 1
    elif labels_match:
        score = min(5, max(3, raw_score))
    else:
        score = min(2, max(1, raw_score))
    return {
        **result,
        "score": score,
        "raw_score": raw_score,
        "rubric_guardrail_applied": score != raw_score,
    }


def run_verbosity_bias_probe(judge: Judge, example: dict[str, str]) -> dict[str, Any]:
    concise = {
        "label": example["expected"],
        "confidence": 0.9,
        "explanation": "La etiqueta aplica el criterio indicado.",
    }
    verbose = {
        "label": example["expected"],
        "confidence": 0.9,
        "explanation": (
            "La decisión coincide con el criterio indicado. Además, se presenta esta explicación "
            "más extensa con contexto general repetido que no modifica la evidencia ni agrega una "
            "razón sustantiva diferente para la clasificación seleccionada."
        ),
    }
    concise_result = judge.evaluate(example, concise)
    verbose_result = judge.evaluate(example, verbose)
    scores_available = (
        concise_result.get("score") is not None and verbose_result.get("score") is not None
    )
    difference = (
        abs(concise_result["score"] - verbose_result["score"])
        if scores_available
        else None
    )
    return {
        "bias": "verbosity",
        "concise_score": concise_result.get("score"),
        "verbose_score": verbose_result.get("score"),
        "absolute_difference": difference,
        "mitigation_effective_threshold": 1,
        "within_threshold": scores_available and difference <= 1,
    }
