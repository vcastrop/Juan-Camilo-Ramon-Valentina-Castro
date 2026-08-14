"""Valida el dataset consensuado y reproduce el split estratificado de ContractRisk."""
from argparse import ArgumentParser
from pathlib import Path
import pandas as pd

SEED = 42
REQUIRED = ["id_contrato", "text", "label_text", "label"]
LABEL_MAP = {"REQUIERE_REVISION": 0, "SUFICIENTE": 1}

def main():
    parser = ArgumentParser()
    parser.add_argument("--input", default="data/contractrisk_dataset_final_etiquetado.csv")
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()
    data = pd.read_csv(args.input, encoding="utf-8-sig")
    if list(data.columns) != REQUIRED:
        raise ValueError(f"Columnas esperadas: {REQUIRED}; recibidas: {data.columns.tolist()}")
    if data["id_contrato"].duplicated().any() or data["text"].duplicated().any():
        raise ValueError("El dataset contiene IDs o textos duplicados")
    expected = data["label_text"].map(LABEL_MAP)
    if expected.isna().any() or not expected.equals(data["label"]):
        raise ValueError("Las etiquetas textuales y numéricas no coinciden")
    # Se replica exactamente el split congelado usado en la evaluación.
    validation_parts = []
    for label, group in data.groupby("label", sort=True):
        validation_parts.append(
            group.sample(n=round(len(group) * 0.20), random_state=SEED + int(label))
        )
    validation = (
        pd.concat(validation_parts, ignore_index=True)
        .sample(frac=1, random_state=SEED)
        .reset_index(drop=True)
    )
    train = (
        data.loc[~data["id_contrato"].isin(set(validation["id_contrato"]))]
        .sample(frac=1, random_state=SEED)
        .reset_index(drop=True)
    )
    if set(train["id_contrato"]) & set(validation["id_contrato"]):
        raise ValueError("Fuga por ID")
    if set(train["text"]) & set(validation["text"]):
        raise ValueError("Fuga por texto")
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    train.to_csv(output / "contractrisk_train.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(output / "contractrisk_validation.csv", index=False, encoding="utf-8-sig")
    print("Train:", len(train), train["label_text"].value_counts().to_dict())
    print("Validation:", len(validation), validation["label_text"].value_counts().to_dict())

if __name__ == "__main__":
    main()
