import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np


RAW_DIR = Path("dataset/raw")
IMAGES_DIR = Path("dataset/images")
LABELS_DIR = Path("dataset/labels")
TEMPLATE_PATH = Path("assets/personagem_template.png")

CLASSE_PLAYER = 0


def encontrar_sugestao(
    imagem: np.ndarray,
    template: np.ndarray | None,
) -> tuple[int, int, int, int] | None:
    if template is None:
        return None

    if (
        template.shape[0] > imagem.shape[0]
        or template.shape[1] > imagem.shape[1]
    ):
        return None

    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    template_cinza = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    resultado = cv2.matchTemplate(
        imagem_cinza,
        template_cinza,
        cv2.TM_CCOEFF_NORMED,
    )

    _, confianca, _, posicao = cv2.minMaxLoc(resultado)

    if confianca < 0.50:
        return None

    x, y = posicao
    h, w = template.shape[:2]

    return x, y, w, h


def limitar_caixa(
    caixa: tuple[int, int, int, int],
    largura: int,
    altura: int,
) -> tuple[int, int, int, int]:
    x, y, w, h = caixa

    x = max(0, min(x, largura - 1))
    y = max(0, min(y, altura - 1))
    w = max(1, min(w, largura - x))
    h = max(1, min(h, altura - y))

    return x, y, w, h


def salvar_rotulo(
    caminho_imagem: Path,
    imagem: np.ndarray,
    caixa: tuple[int, int, int, int] | None,
) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_DIR.mkdir(parents=True, exist_ok=True)

    destino_imagem = IMAGES_DIR / caminho_imagem.name
    destino_label = LABELS_DIR / f"{caminho_imagem.stem}.txt"

    shutil.copy2(caminho_imagem, destino_imagem)

    if caixa is None:
        destino_label.write_text("", encoding="utf-8")
        return

    altura_img, largura_img = imagem.shape[:2]
    x, y, w, h = limitar_caixa(
        caixa,
        largura_img,
        altura_img,
    )

    centro_x = (x + w / 2) / largura_img
    centro_y = (y + h / 2) / altura_img
    largura_norm = w / largura_img
    altura_norm = h / altura_img

    linha = (
        f"{CLASSE_PLAYER} "
        f"{centro_x:.6f} "
        f"{centro_y:.6f} "
        f"{largura_norm:.6f} "
        f"{altura_norm:.6f}\n"
    )

    destino_label.write_text(
        linha,
        encoding="utf-8",
    )


def selecionar_caixa(
    imagem: np.ndarray,
    sugestao: tuple[int, int, int, int] | None,
    nome: str,
) -> tuple[str, tuple[int, int, int, int] | None]:
    estado = {
        "inicio": None,
        "fim": None,
        "arrastando": False,
        "caixa": sugestao,
    }

    janela = "SlayerAI - Rotulador"

    def mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            estado["inicio"] = (x, y)
            estado["fim"] = (x, y)
            estado["arrastando"] = True

        elif event == cv2.EVENT_MOUSEMOVE and estado["arrastando"]:
            estado["fim"] = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            estado["fim"] = (x, y)
            estado["arrastando"] = False

            x1, y1 = estado["inicio"]
            x2, y2 = estado["fim"]

            esquerda = min(x1, x2)
            topo = min(y1, y2)
            direita = max(x1, x2)
            baixo = max(y1, y2)

            if direita - esquerda > 2 and baixo - topo > 2:
                estado["caixa"] = (
                    esquerda,
                    topo,
                    direita - esquerda,
                    baixo - topo,
                )

    cv2.namedWindow(janela)
    cv2.setMouseCallback(janela, mouse)

    while True:
        preview = imagem.copy()

        caixa = estado["caixa"]

        if estado["arrastando"]:
            x1, y1 = estado["inicio"]
            x2, y2 = estado["fim"]
            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                (0, 255, 255),
                2,
            )

        if caixa is not None:
            x, y, w, h = caixa
            cv2.rectangle(
                preview,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2,
            )

        cv2.putText(
            preview,
            nome,
            (10, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            preview,
            "Mouse: caixa | ENTER: salvar | N: sem player | R: limpar | Q: sair",
            (10, preview.shape[0] - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(janela, preview)

        tecla = cv2.waitKey(20) & 0xFF

        if tecla in (13, 32):
            if estado["caixa"] is None:
                print(
                    "Nenhuma caixa definida. "
                    "Desenhe o player com o mouse ou pressione N "
                    "se o personagem realmente nao estiver visivel."
                )
                continue

            return "salvar", estado["caixa"]

        if tecla == ord("n"):
            return "salvar", None

        if tecla == ord("r"):
            estado["caixa"] = None

        if tecla == ord("q"):
            return "sair", None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rotula frames do SlayerAI no formato YOLO."
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=0,
        help="Quantidade maxima para rotular nesta sessao. 0 = sem limite.",
    )
    parser.add_argument(
        "--refazer",
        action="store_true",
        help="Mostra novamente imagens que ja possuem rotulo.",
    )
    args = parser.parse_args()

    arquivos = sorted(RAW_DIR.glob("*.png"))

    if not arquivos:
        print("Nenhum frame encontrado em dataset/raw.")
        return

    template = cv2.imread(str(TEMPLATE_PATH))
    if template is None:
        template = None
        print("Template local nao encontrado. Rotulagem sera totalmente manual.")
    else:
        print("Template local encontrado. Sugestoes automaticas ativadas.")

    processados = 0

    try:
        for indice, caminho in enumerate(arquivos, start=1):
            label_existente = LABELS_DIR / f"{caminho.stem}.txt"

            if label_existente.exists() and not args.refazer:
                continue

            imagem = cv2.imread(str(caminho))

            if imagem is None:
                print(f"Ignorando arquivo invalido: {caminho}")
                continue

            sugestao = encontrar_sugestao(
                imagem,
                template,
            )

            print(
                f"[{indice}/{len(arquivos)}] {caminho.name}"
            )

            acao, caixa = selecionar_caixa(
                imagem,
                sugestao,
                caminho.name,
            )

            if acao == "sair":
                break

            salvar_rotulo(
                caminho,
                imagem,
                caixa,
            )

            processados += 1
            print(
                f"Rotulo salvo: {caminho.stem}.txt"
            )

            if args.limite > 0 and processados >= args.limite:
                break

    finally:
        cv2.destroyAllWindows()

    print(
        f"Sessao finalizada. {processados} imagem(ns) rotulada(s)."
    )


if __name__ == "__main__":
    main()
