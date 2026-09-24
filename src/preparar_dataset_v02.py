import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "dataset_v02/images"
LABELS_DIR = ROOT / "dataset_v02/labels"
TRAIN_IMAGES = ROOT / "dataset_v02/train/images"
TRAIN_LABELS = ROOT / "dataset_v02/train/labels"
VAL_IMAGES = ROOT / "dataset_v02/val/images"
VAL_LABELS = ROOT / "dataset_v02/val/labels"


def limpar_destino() -> None:
    for pasta in (
        TRAIN_IMAGES,
        TRAIN_LABELS,
        VAL_IMAGES,
        VAL_LABELS,
    ):
        if pasta.exists():
            shutil.rmtree(pasta)

        pasta.mkdir(
            parents=True,
            exist_ok=True,
        )


def copiar_par(
    imagem: Path,
    destino_imagem: Path,
    destino_label: Path,
) -> None:
    label = (
        LABELS_DIR
        / f"{imagem.stem}.txt"
    )

    if not label.exists():
        raise FileNotFoundError(
            f"Label ausente para {imagem.name}: "
            f"{label}"
        )

    shutil.copy2(
        imagem,
        destino_imagem / imagem.name,
    )
    shutil.copy2(
        label,
        destino_label / label.name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Divide o dataset v0.2 por sessao, "
            "evitando vazamento temporal."
        )
    )
    parser.add_argument(
        "--val-prefixo",
        required=True,
        help=(
            "Prefixo da sessao reservada para "
            "validacao. Ex.: frame"
        ),
    )
    args = parser.parse_args()

    imagens = sorted(
        IMAGES_DIR.glob("*.png")
    )

    if not imagens:
        print(
            "Nenhuma imagem rotulada em "
            "dataset_v02/images."
        )
        return

    prefixo = (
        args.val_prefixo.rstrip("_")
        + "_"
    )

    val = [
        imagem
        for imagem in imagens
        if imagem.name.startswith(prefixo)
    ]

    train = [
        imagem
        for imagem in imagens
        if not imagem.name.startswith(prefixo)
    ]

    if not val:
        raise ValueError(
            "Nenhuma imagem corresponde ao "
            f"prefixo de validacao: {prefixo}"
        )

    if not train:
        raise ValueError(
            "Nenhuma imagem sobrou para treino."
        )

    limpar_destino()

    for imagem in train:
        copiar_par(
            imagem,
            TRAIN_IMAGES,
            TRAIN_LABELS,
        )

    for imagem in val:
        copiar_par(
            imagem,
            VAL_IMAGES,
            VAL_LABELS,
        )

    print("SlayerAI - Split dataset v0.2")
    print("=" * 40)
    print(
        "Validacao reservada por sessao: "
        f"{args.val_prefixo}"
    )
    print(f"Treino: {len(train)} imagem(ns)")
    print(
        f"Validacao: {len(val)} imagem(ns)"
    )
    print(
        "Nenhuma imagem da sessao de validacao "
        "foi usada no treino."
    )


if __name__ == "__main__":
    main()
