import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np

from detector import DetectorPlayer
from visao_utils import ROI


RAW_DIR = Path("dataset_v02/raw")
IMAGES_DIR = Path("dataset_v02/images")
LABELS_DIR = Path("dataset_v02/labels")
MODELO_PLAYER = Path("modelos/player_v01.onnx")

CLASSE_PLAYER = 0
CLASSE_INIMIGO = 1

NOMES_CLASSES = {
    CLASSE_PLAYER: "player",
    CLASSE_INIMIGO: "inimigo",
}

CORES = {
    CLASSE_PLAYER: (0, 255, 0),
    CLASSE_INIMIGO: (0, 0, 255),
}


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


def caixa_para_yolo(
    classe: int,
    caixa: tuple[int, int, int, int],
    largura_img: int,
    altura_img: int,
) -> str:
    x, y, w, h = limitar_caixa(
        caixa,
        largura_img,
        altura_img,
    )

    centro_x = (x + w / 2) / largura_img
    centro_y = (y + h / 2) / altura_img
    largura_norm = w / largura_img
    altura_norm = h / altura_img

    return (
        f"{classe} "
        f"{centro_x:.8f} "
        f"{centro_y:.8f} "
        f"{largura_norm:.8f} "
        f"{altura_norm:.8f}"
    )


def yolo_para_caixa(
    linha: str,
    largura_img: int,
    altura_img: int,
) -> tuple[int, tuple[int, int, int, int]]:
    partes = linha.split()

    if len(partes) != 5:
        raise ValueError("Linha YOLO invalida.")

    classe = int(partes[0])
    centro_x = float(partes[1]) * largura_img
    centro_y = float(partes[2]) * altura_img
    largura = float(partes[3]) * largura_img
    altura = float(partes[4]) * altura_img

    x = int(round(centro_x - largura / 2))
    y = int(round(centro_y - altura / 2))
    w = int(round(largura))
    h = int(round(altura))

    return classe, limitar_caixa(
        (x, y, w, h),
        largura_img,
        altura_img,
    )


def carregar_rotulos(
    caminho: Path,
    largura: int,
    altura: int,
) -> list[tuple[int, tuple[int, int, int, int]]]:
    if not caminho.exists():
        return []

    conteudo = caminho.read_text(
        encoding="utf-8"
    ).strip()

    if not conteudo:
        return []

    caixas = []

    for linha in conteudo.splitlines():
        caixas.append(
            yolo_para_caixa(
                linha,
                largura,
                altura,
            )
        )

    return caixas


def salvar_rotulos(
    caminho_imagem: Path,
    imagem: np.ndarray,
    caixas: list[
        tuple[int, tuple[int, int, int, int]]
    ],
) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_DIR.mkdir(parents=True, exist_ok=True)

    destino_imagem = (
        IMAGES_DIR / caminho_imagem.name
    )
    destino_label = (
        LABELS_DIR
        / f"{caminho_imagem.stem}.txt"
    )

    shutil.copy2(
        caminho_imagem,
        destino_imagem,
    )

    altura, largura = imagem.shape[:2]
    linhas = [
        caixa_para_yolo(
            classe,
            caixa,
            largura,
            altura,
        )
        for classe, caixa in caixas
    ]

    texto = (
        "\n".join(linhas) + "\n"
        if linhas
        else ""
    )

    destino_label.write_text(
        texto,
        encoding="utf-8",
    )


def sugerir_player(
    detector: DetectorPlayer | None,
    imagem: np.ndarray,
) -> tuple[int, int, int, int] | None:
    if detector is None:
        return None

    deteccao = detector.detectar(imagem)

    if deteccao is None:
        return None

    x1, y1, x2, y2 = deteccao.caixa
    largura = imagem.shape[1]
    centro_x = (x1 + x2) / 2

    if centro_x / largura > 0.14:
        return None

    return (
        x1,
        y1,
        x2 - x1,
        y2 - y1,
    )


def selecionar_caixas(
    imagem: np.ndarray,
    nome: str,
    iniciais: list[
        tuple[int, tuple[int, int, int, int]]
    ],
) -> tuple[
    str,
    list[
        tuple[int, tuple[int, int, int, int]]
    ],
]:
    estado = {
        "inicio": None,
        "fim": None,
        "arrastando": False,
        "classe": CLASSE_INIMIGO,
        "caixas": list(iniciais),
    }

    janela = "SlayerAI - Rotulador v0.2"

    def remover_caixa_em(x: int, y: int) -> None:
        candidatos = []

        for indice, (_, caixa) in enumerate(
            estado["caixas"]
        ):
            bx, by, bw, bh = caixa

            if (
                bx <= x <= bx + bw
                and by <= y <= by + bh
            ):
                area = bw * bh
                candidatos.append(
                    (area, indice)
                )

        if not candidatos:
            return

        _, indice = min(candidatos)
        estado["caixas"].pop(indice)

    def mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            estado["inicio"] = (x, y)
            estado["fim"] = (x, y)
            estado["arrastando"] = True

        elif (
            event == cv2.EVENT_MOUSEMOVE
            and estado["arrastando"]
        ):
            estado["fim"] = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            if estado["inicio"] is None:
                return

            estado["fim"] = (x, y)
            estado["arrastando"] = False

            x1, y1 = estado["inicio"]
            x2, y2 = estado["fim"]

            esquerda = min(x1, x2)
            topo = min(y1, y2)
            direita = max(x1, x2)
            baixo = max(y1, y2)

            if (
                direita - esquerda > 2
                and baixo - topo > 2
            ):
                estado["caixas"].append(
                    (
                        estado["classe"],
                        (
                            esquerda,
                            topo,
                            direita - esquerda,
                            baixo - topo,
                        ),
                    )
                )

        elif event == cv2.EVENT_RBUTTONDOWN:
            remover_caixa_em(x, y)

    cv2.namedWindow(
        janela,
        cv2.WINDOW_NORMAL,
    )
    cv2.setMouseCallback(
        janela,
        mouse,
    )

    while True:
        preview = imagem.copy()

        for classe, caixa in estado["caixas"]:
            x, y, w, h = caixa
            cor = CORES.get(
                classe,
                (255, 255, 255),
            )
            nome_classe = NOMES_CLASSES.get(
                classe,
                str(classe),
            )

            cv2.rectangle(
                preview,
                (x, y),
                (x + w, y + h),
                cor,
                2,
            )
            cv2.putText(
                preview,
                nome_classe,
                (x, max(18, y - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                cor,
                2,
                cv2.LINE_AA,
            )

        if (
            estado["arrastando"]
            and estado["inicio"] is not None
            and estado["fim"] is not None
        ):
            x1, y1 = estado["inicio"]
            x2, y2 = estado["fim"]
            cor = CORES[
                estado["classe"]
            ]

            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                cor,
                2,
            )

        ativa = NOMES_CLASSES[
            estado["classe"]
        ].upper()

        cv2.rectangle(
            preview,
            (0, 0),
            (preview.shape[1], 62),
            (0, 0, 0),
            -1,
        )

        cv2.putText(
            preview,
            (
                f"{nome} | ativa: {ativa} | "
                f"caixas: {len(estado['caixas'])}"
            ),
            (10, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            CORES[estado["classe"]],
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            preview,
            (
                "P player | I inimigo | "
                "mouse esq adiciona | dir remove | "
                "Z desfaz | R limpa"
            ),
            (10, 44),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.putText(
            preview,
            "ENTER salva | Q sai",
            (10, preview.shape[0] - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(
            janela,
            preview,
        )

        tecla = cv2.waitKey(20) & 0xFF

        if tecla == ord("p"):
            estado["classe"] = CLASSE_PLAYER
            continue

        if tecla == ord("i"):
            estado["classe"] = CLASSE_INIMIGO
            continue

        if tecla == ord("z"):
            if estado["caixas"]:
                estado["caixas"].pop()
            continue

        if tecla == ord("r"):
            estado["caixas"].clear()
            continue

        if tecla in (13, 32):
            tem_player = any(
                classe == CLASSE_PLAYER
                for classe, _ in estado["caixas"]
            )

            if not tem_player:
                print(
                    "Falta marcar o player. "
                    "Pressione P e desenhe a caixa."
                )
                continue

            return "salvar", list(
                estado["caixas"]
            )

        if tecla == ord("q"):
            return "sair", list(
                estado["caixas"]
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rotula player e inimigos com multiplas "
            "caixas por frame para a v0.2."
        )
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=0,
        help=(
            "Quantidade maxima nesta sessao. "
            "0 = sem limite."
        ),
    )
    parser.add_argument(
        "--refazer",
        action="store_true",
        help=(
            "Abre novamente imagens que ja possuem "
            "rotulo."
        ),
    )
    parser.add_argument(
        "--sem-sugestao-player",
        action="store_true",
        help=(
            "Nao usa o detector v0.1 para sugerir "
            "a caixa do player."
        ),
    )
    parser.add_argument(
        "--prefixo",
        default=None,
        help=(
            "Rotula apenas arquivos de uma sessao. "
            "Ex.: --prefixo sessao2"
        ),
    )
    args = parser.parse_args()

    padrao = (
        f"{args.prefixo}_*.png"
        if args.prefixo
        else "*.png"
    )

    arquivos = sorted(
        RAW_DIR.glob(padrao)
    )

    if not arquivos:
        print(
            "Nenhum frame encontrado em "
            "dataset_v02/raw para o filtro informado."
        )
        return

    detector = None

    if (
        not args.sem_sugestao_player
        and MODELO_PLAYER.exists()
    ):
        try:
            detector = DetectorPlayer(
                modelo=MODELO_PLAYER,
                conf=0.30,
                imgsz=320,
                roi=ROI(
                    x=0.0,
                    y=0.0,
                    largura=0.30,
                    altura=1.0,
                ),
                suavizacao=1.0,
            )
            print(
                "Sugestao automatica do player: ATIVA"
            )
        except Exception as erro:
            print(
                "Nao foi possivel ativar a sugestao "
                f"do player: {erro}"
            )
            detector = None

    processados = 0

    try:
        for indice, caminho in enumerate(
            arquivos,
            start=1,
        ):
            destino_label = (
                LABELS_DIR
                / f"{caminho.stem}.txt"
            )

            if (
                destino_label.exists()
                and not args.refazer
            ):
                continue

            imagem = cv2.imread(
                str(caminho)
            )

            if imagem is None:
                print(
                    f"Ignorando arquivo invalido: "
                    f"{caminho}"
                )
                continue

            altura, largura = imagem.shape[:2]

            existentes = carregar_rotulos(
                destino_label,
                largura,
                altura,
            )

            if not existentes:
                sugestao = sugerir_player(
                    detector,
                    imagem,
                )

                if sugestao is not None:
                    existentes.append(
                        (
                            CLASSE_PLAYER,
                            sugestao,
                        )
                    )

            print(
                f"[{indice}/{len(arquivos)}] "
                f"{caminho.name}"
            )

            acao, caixas = selecionar_caixas(
                imagem,
                caminho.name,
                existentes,
            )

            if acao == "sair":
                break

            salvar_rotulos(
                caminho,
                imagem,
                caixas,
            )

            processados += 1

            player = sum(
                1
                for classe, _ in caixas
                if classe == CLASSE_PLAYER
            )
            inimigos = sum(
                1
                for classe, _ in caixas
                if classe == CLASSE_INIMIGO
            )

            print(
                "Rotulo salvo: "
                f"{caminho.stem}.txt | "
                f"player={player} | "
                f"inimigos={inimigos}"
            )

            if (
                args.limite > 0
                and processados >= args.limite
            ):
                break

    finally:
        cv2.destroyAllWindows()

    print(
        "Sessao finalizada. "
        f"{processados} imagem(ns) rotulada(s)."
    )


if __name__ == "__main__":
    main()
