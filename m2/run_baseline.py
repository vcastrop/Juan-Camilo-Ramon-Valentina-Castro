"""Ejecuta el harness M2 sobre el adapter RoBERTalex + LoRA de M1."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

from harness import (
    HarnessConfig,
    TransformersRubricJudge,
    harness,
    load_eval_set,
    run_verbosity_bias_probe,
)
from systems import LoraContractRiskSystem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", default="m2/eval/contractrisk_m2_eval_gold.csv")
    parser.add_argument("--adapter", default="model/contractrisk_robertalex_lora_adapter.zip")
    parser.add_argument("--rubric", default="m2/rubrics/judge_rubric_v1_2.json")
    parser.add_argument("--output-dir", default="m2/results")
    parser.add_argument("--judge-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = HarnessConfig(seed=args.seed)
    eval_rows = load_eval_set(args.eval_set)

    baseline = LoraContractRiskSystem(args.adapter, seed=args.seed)
    raw_predictions = baseline.predict_many(
        [row["descripcion_del_proceso"] for row in eval_rows]
    )
    baseline.release()

    class FrozenPredictions:
        def predict_many(self, texts):
            if len(texts) != len(raw_predictions):
                raise ValueError("El eval set cambió después de ejecutar el baseline.")
            return raw_predictions

    judge = TransformersRubricJudge(
        rubric_path=args.rubric,
        model_id=args.judge_model,
        seed=args.seed,
    )
    result = harness(
        eval_set=eval_rows,
        system=FrozenPredictions(),
        judge=judge,
        output_dir=args.output_dir,
        config=config,
    )
    bias_probe = run_verbosity_bias_probe(judge, eval_rows[0])
    output_dir = Path(args.output_dir)
    with (output_dir / "judge_bias_probe.json").open("w", encoding="utf-8") as handle:
        json.dump(bias_probe, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    def sha256(path: str) -> str:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    import torch

    metadata = {
        "seed": args.seed,
        "eval_set": args.eval_set,
        "eval_set_sha256": sha256(args.eval_set),
        "adapter": args.adapter,
        "adapter_sha256": sha256(args.adapter),
        "base_model": "BSC-LT/RoBERTalex",
        "judge_model": args.judge_model,
        "rubric": args.rubric,
        "rubric_sha256": sha256(args.rubric),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "transformers_version": importlib.metadata.version("transformers"),
        "peft_version": importlib.metadata.version("peft"),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
    }
    with (output_dir / "run_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps({"metrics": result["metrics"], "bias_probe": bias_probe}, indent=2))


if __name__ == "__main__":
    main()
