import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "dataset_v02/images"
LABELS_DIR = ROOT / "dataset_v02/labels"

CLASSES_VALIDAS = {
    0: "player",
    1: "inimigo",
}

# Labels YOLO sao salvos em ponto flutuante. Uma caixa encostada
# exatamente na borda pode ultrapassar 0..1 por poucos milionésimos
# depois do arredondamento decimal, sem estar realmente fora da imagem.
TOLERANCIA_BORDA = 1e-5


def validar_linha_yolo(
    linha: str,
) -> tuple[bool, str | None, int | None]:
    partes = linha.split()

    if len(partes) != 5:
        return False, "rotulo deve ter 5 campos", None

    try:
        classe = int(partes[0])
        valores = [
            float(valor)
            for valor in partes[1:]
        ]
    except ValueError:
        return False, "campos numericos invalidos", None

    if classe not in CLASSES_VALIDAS:
        return (
            False,
            f"classe inesperada: {classe}",
            classe,
        )

    if any(
        valor < 0 or valor > 1
        for valor in valores
    ):
        return (
            False,
            "coordenada fora do intervalo 0..1",
            classe,
        )

    centro_x, centro_y, largura, altura = valores

    if largura <= 0 or altura <= 0:
        return (
            False,
            "largura/altura devem ser positivas",
            classe,
        )

    if centro_x - largura / 2 < -TOLERANCIA_BORDA:
        return (
            False,
            "caixa ultrapassa a borda esquerda",
            classe,
        )

    if centro_x + largura / 2 > 1 + TOLERANCIA_BORDA:
        return (
            False,
            "caixa ultrapassa a borda direita",
            classe,
        )

    if centro_y - altura / 2 < -TOLERANCIA_BORDA:
        return (
            False,
            "caixa ultrapassa a borda superior",
            classe,
        )

    if centro_y + altura / 2 > 1 + TOLERANCIA_BORDA:
        return (
            False,
            "caixa ultrapassa a borda inferior",
            classe,
        )

    return True, None, classe


def validar_dataset() -> tuple[
    list[str],
    Counter[int],
    int,
]:
    erros = []
    classes: Counter[int] = Counter()
    frames_sem_inimigo = 0

    imagens = {
        caminho.stem: caminho
        for caminho in IMAGES_DIR.glob("*.png")
    }
    labels = {
        caminho.stem: caminho
        for caminho in LABELS_DIR.glob("*.txt")
    }

    for stem in sorted(imagens):
        if stem not in labels:
            erros.append(
                f"Label ausente para {imagens[stem].name}"
            )

    for stem in sorted(labels):
        if stem not in imagens:
            erros.append(
                f"Imagem ausente para {labels[stem].name}"
            )
            continue

        conteudo = labels[stem].read_text(
            encoding="utf-8"
        ).strip()

        if not conteudo:
            erros.append(
                f"{labels[stem].name}: label vazio"
            )
            continue

        classes_frame: Counter[int] = Counter()

        for numero, linha in enumerate(
            conteudo.splitlines(),
            start=1,
        ):
            valido, motivo, classe = (
                validar_linha_yolo(linha)
            )

            if not valido:
                erros.append(
                    f"{labels[stem].name}:{numero}: "
                    f"{motivo}"
                )
                continue

            if classe is not None:
                classes[classe] += 1
                classes_frame[classe] += 1

        players = classes_frame.get(0, 0)

        if players != 1:
            erros.append(
                f"{labels[stem].name}: esperado 1 player, "
                f"encontrado {players}"
            )

        if classes_frame.get(1, 0) == 0:
            frames_sem_inimigo += 1

    return erros, classes, frames_sem_inimigo


def main() -> None:
    imagens = list(
        IMAGES_DIR.glob("*.png")
    )
    labels = list(
        LABELS_DIR.glob("*.txt")
    )

    erros, classes, frames_sem_inimigo = (
        validar_dataset()
    )

    print("SlayerAI - Validacao dataset v0.2")
    print("=" * 40)
    print(f"Imagens rotuladas: {len(imagens)}")
    print(f"Labels: {len(labels)}")

    for classe, nome in CLASSES_VALIDAS.items():
        print(
            f"Caixas de {nome}: "
            f"{classes.get(classe, 0)}"
        )

    print(
        "Frames sem inimigo: "
        f"{frames_sem_inimigo}"
    )

    if erros:
        print("")
        print(
            f"Erros encontrados: {len(erros)}"
        )

        for erro in erros[:40]:
            print(f"- {erro}")

        if len(erros) > 40:
            print(
                "... e mais "
                f"{len(erros) - 40} erro(s)."
            )

        sys.exit(1)

    print("Dataset v0.2 consistente.")


if __name__ == "__main__":
    main()
