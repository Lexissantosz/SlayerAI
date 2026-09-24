from collections import Counter
from pathlib import Path


RAW_DIR = Path("dataset_v02/raw")
LABELS_DIR = Path("dataset_v02/labels")

NOMES = {
    0: "player",
    1: "inimigo",
}


def contar_classes(caminho: Path) -> Counter[int]:
    contagem: Counter[int] = Counter()

    if not caminho.exists():
        return contagem

    conteudo = caminho.read_text(
        encoding="utf-8"
    ).strip()

    if not conteudo:
        return contagem

    for linha in conteudo.splitlines():
        partes = linha.split()

        if not partes:
            continue

        try:
            classe = int(partes[0])
        except ValueError:
            continue

        contagem[classe] += 1

    return contagem


def main() -> None:
    raws = sorted(RAW_DIR.glob("*.png"))
    labels = sorted(LABELS_DIR.glob("*.txt"))

    total_raw = len(raws)
    total_labels = len(labels)

    classes: Counter[int] = Counter()
    frames_com_inimigo = 0
    frames_sem_inimigo = 0
    max_inimigos = 0

    for label in labels:
        contagem = contar_classes(label)
        classes.update(contagem)

        inimigos = contagem.get(1, 0)

        if inimigos > 0:
            frames_com_inimigo += 1
        else:
            frames_sem_inimigo += 1

        max_inimigos = max(
            max_inimigos,
            inimigos,
        )

    percentual = (
        total_labels / total_raw * 100
        if total_raw
        else 0.0
    )

    media_inimigos = (
        classes.get(1, 0) / total_labels
        if total_labels
        else 0.0
    )

    print("SlayerAI - Resumo dataset v0.2")
    print("=" * 40)
    print(f"Frames coletados: {total_raw}")
    print(
        f"Frames rotulados: {total_labels} "
        f"({percentual:.1f}%)"
    )

    print("")
    print("Caixas por classe:")

    for classe in sorted(classes):
        nome = NOMES.get(
            classe,
            f"classe_{classe}",
        )
        print(
            f"- {nome}: {classes[classe]}"
        )

    print("")
    print(
        "Frames com inimigo: "
        f"{frames_com_inimigo}"
    )
    print(
        "Frames sem inimigo: "
        f"{frames_sem_inimigo}"
    )
    print(
        "Media de inimigos por frame rotulado: "
        f"{media_inimigos:.2f}"
    )
    print(
        "Maximo de inimigos em um frame: "
        f"{max_inimigos}"
    )


if __name__ == "__main__":
    main()
