import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "dataset/images"
LABELS_DIR = ROOT / "dataset/labels"


def validar_linha_yolo(
    linha: str,
) -> tuple[bool, str | None]:
    partes = linha.split()

    if len(partes) != 5:
        return False, "rotulo deve ter 5 campos"

    try:
        classe = int(partes[0])
        valores = [float(valor) for valor in partes[1:]]
    except ValueError:
        return False, "campos numericos invalidos"

    if classe != 0:
        return False, f"classe inesperada: {classe}"

    if any(valor < 0 or valor > 1 for valor in valores):
        return False, "coordenada fora do intervalo 0..1"

    centro_x, centro_y, largura, altura = valores

    if largura <= 0 or altura <= 0:
        return False, "largura/altura devem ser positivas"

    if centro_x - largura / 2 < 0:
        return False, "caixa ultrapassa a borda esquerda"

    if centro_x + largura / 2 > 1:
        return False, "caixa ultrapassa a borda direita"

    if centro_y - altura / 2 < 0:
        return False, "caixa ultrapassa a borda superior"

    if centro_y + altura / 2 > 1:
        return False, "caixa ultrapassa a borda inferior"

    return True, None


def validar_dataset() -> list[str]:
    erros = []

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
            continue

        for numero, linha in enumerate(
            conteudo.splitlines(),
            start=1,
        ):
            valido, motivo = validar_linha_yolo(linha)

            if not valido:
                erros.append(
                    f"{labels[stem].name}:{numero}: {motivo}"
                )

    return erros


def main() -> None:
    imagens = list(IMAGES_DIR.glob("*.png"))
    labels = list(LABELS_DIR.glob("*.txt"))
    vazios = 0

    for caminho in labels:
        if not caminho.read_text(
            encoding="utf-8"
        ).strip():
            vazios += 1

    erros = validar_dataset()

    print(f"Imagens: {len(imagens)}")
    print(f"Labels: {len(labels)}")
    print(f"Labels sem player: {vazios}")

    if erros:
        print("")
        print(f"Erros encontrados: {len(erros)}")

        for erro in erros[:30]:
            print(f"- {erro}")

        if len(erros) > 30:
            print(
                f"... e mais {len(erros) - 30} erro(s)."
            )

        sys.exit(1)

    print("Dataset consistente.")


if __name__ == "__main__":
    main()
