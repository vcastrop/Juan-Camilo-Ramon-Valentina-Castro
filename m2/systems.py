"""Adaptadores de sistemas evaluables por el harness."""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

from harness import ALLOWED_LABELS, set_seed


class LoraContractRiskSystem:
    """Carga el adapter M1 y expone la interfaz común ``predict_many``."""

    def __init__(
        self,
        adapter_path: str | Path,
        batch_size: int = 16,
        max_length: int = 256,
        seed: int = 42,
    ) -> None:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        set_seed(seed)
        self.torch = torch
        self.batch_size = batch_size
        self.max_length = max_length
        self._temporary_directory: tempfile.TemporaryDirectory[str] | None = None
        adapter_path = Path(adapter_path)
        if adapter_path.suffix.lower() == ".zip":
            self._temporary_directory = tempfile.TemporaryDirectory(prefix="contractrisk_adapter_")
            with zipfile.ZipFile(adapter_path) as archive:
                archive.extractall(self._temporary_directory.name)
            children = list(Path(self._temporary_directory.name).iterdir())
            adapter_path = children[0] if len(children) == 1 and children[0].is_dir() else Path(self._temporary_directory.name)

        config = json.loads((adapter_path / "adapter_config.json").read_text(encoding="utf-8"))
        base_model_id = config["base_model_name_or_path"]
        self.tokenizer = AutoTokenizer.from_pretrained(adapter_path)
        base_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_id,
            num_labels=2,
            id2label={0: "REQUIERE_REVISION", 1: "SUFICIENTE"},
            label2id={"REQUIERE_REVISION": 0, "SUFICIENTE": 1},
        )
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device).eval()

    def predict_many(self, texts: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            ).to(self.device)
            with self.torch.no_grad():
                logits = self.model(**encoded).logits
                probabilities = self.torch.softmax(logits, dim=-1).cpu().numpy()
            for row in probabilities:
                predicted_id = int(np.argmax(row))
                results.append(
                    {
                        "label": ALLOWED_LABELS[predicted_id],
                        "confidence": float(row[predicted_id]),
                        "explanation": "",
                    }
                )
        return results

    def release(self) -> None:
        self.model.to("cpu")
        if self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
