import argparse
import random
import shutil
from pathlib import Path


IMAGES_DIR = Path("dataset/images")
LABELS_DIR = Path("dataset/labels")
TRAIN_IMAGES = Path("dataset/train/images")
TRAIN_LABELS = Path("dataset/train/labels")
VAL_IMAGES = Path("dataset/val/images")
VAL_LABELS = Path("dataset/val/labels")


def limpar_destino() -> None:
    for pasta in (
        TRAIN_IMAGES,
        TRAIN_LABELS,
        VAL_IMAGES,
        VAL_LABELS,
    ):
        if pasta.exists():
            shutil.rmtree(pasta)
        pasta.mkdir(parents=True, exist_ok=True)


def copiar_par(
    imagem: Path,
    destino_imagem: Path,
    destino_label: Path,
) -> None:
    label = LABELS_DIR / f"{imagem.stem}.txt"

    if not label.exists():
        raise FileNotFoundError(
            f"Label ausente para {imagem.name}: {label}"
        )

    shutil.copy2(imagem, destino_imagem / imagem.name)
    shutil.copy2(label, destino_label / label.name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Divide o dataset rotulado em treino e validacao."
    )
    parser.add_argument(
        "--val",
        type=float,
        default=0.20,
        help="Fracao do dataset reservada para validacao.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente para reproducibilidade.",
    )
    args = parser.parse_args()

    imagens = sorted(IMAGES_DIR.glob("*.png"))

    if len(imagens) < 10:
        print(
            "Dataset pequeno demais. "
            "Rotule pelo menos 10 imagens antes de dividir."
        )
        return

    if not 0.05 <= args.val <= 0.50:
        raise ValueError("--val deve estar entre 0.05 e 0.50")

    random.seed(args.seed)
    random.shuffle(imagens)

    quantidade_val = max(
        1,
        round(len(imagens) * args.val),
    )

    val = imagens[:quantidade_val]
    train = imagens[quantidade_val:]

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

    print(f"Treino: {len(train)} imagem(ns)")
    print(f"Validacao: {len(val)} imagem(ns)")
    print("Dataset dividido com sucesso.")


if __name__ == "__main__":
    main()
