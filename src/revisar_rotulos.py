import argparse
from pathlib import Path

import cv2


IMAGES_DIR = Path("dataset/images")
LABELS_DIR = Path("dataset/labels")


def ler_caixas(
    caminho_label: Path,
    largura: int,
    altura: int,
) -> list[tuple[int, int, int, int, int]]:
    if not caminho_label.exists():
        return []

    conteudo = caminho_label.read_text(
        encoding="utf-8"
    ).strip()

    if not conteudo:
        return []

    caixas = []

    for linha in conteudo.splitlines():
        partes = linha.split()

        if len(partes) != 5:
            continue

        classe = int(partes[0])
        centro_x = float(partes[1]) * largura
        centro_y = float(partes[2]) * altura
        largura_box = float(partes[3]) * largura
        altura_box = float(partes[4]) * altura

        x1 = int(centro_x - largura_box / 2)
        y1 = int(centro_y - altura_box / 2)
        x2 = int(centro_x + largura_box / 2)
        y2 = int(centro_y + altura_box / 2)

        caixas.append(
            (classe, x1, y1, x2, y2)
        )

    return caixas


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Revisa visualmente os rotulos YOLO do dataset."
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=20,
        help="Quantidade maxima de imagens para revisar.",
    )
    args = parser.parse_args()

    imagens = sorted(IMAGES_DIR.glob("*.png"))

    if not imagens:
        print("Nenhuma imagem rotulada encontrada em dataset/images.")
        return

    total = min(args.limite, len(imagens))

    print("Revisao de rotulos iniciada.")
    print("A/D ou setas = navegar | Q = sair")

    indice = 0

    while 0 <= indice < total:
        caminho_imagem = imagens[indice]
        imagem = cv2.imread(str(caminho_imagem))

        if imagem is None:
            indice += 1
            continue

        altura, largura = imagem.shape[:2]
        caminho_label = LABELS_DIR / f"{caminho_imagem.stem}.txt"

        caixas = ler_caixas(
            caminho_label,
            largura,
            altura,
        )

        preview = imagem.copy()

        if not caixas:
            cv2.putText(
                preview,
                "SEM PLAYER",
                (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        for classe, x1, y1, x2, y2 in caixas:
            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                preview,
                f"player ({classe})",
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        cv2.putText(
            preview,
            f"{indice + 1}/{total} - {caminho_imagem.name}",
            (10, preview.shape[0] - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(
            "SlayerAI - Revisao de rotulos",
            preview,
        )

        tecla = cv2.waitKey(0) & 0xFF

        if tecla == ord("q"):
            break

        if tecla in (
            ord("d"),
            83,
        ):
            indice += 1
            continue

        if tecla in (
            ord("a"),
            81,
        ):
            indice = max(0, indice - 1)
            continue

    cv2.destroyAllWindows()
    print("Revisao finalizada.")


if __name__ == "__main__":
    main()
