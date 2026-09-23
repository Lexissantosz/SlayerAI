import argparse
import time
from pathlib import Path

import cv2

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from detector import DetectorPlayer
from memoria_deteccao import MemoriaDeteccao
from visao_utils import (
    calcular_roi_pixels,
    parse_roi,
)


ROOT = Path(__file__).resolve().parent.parent
MODELO_ONNX = ROOT / "modelos/player_v01.onnx"
MODELO_PT = ROOT / "modelos/player_v01_best.pt"
MODELO_PADRAO = MODELO_ONNX if MODELO_ONNX.exists() else MODELO_PT


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Testa o detector do personagem em tempo real."
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO_PADRAO),
        help="Caminho do modelo .pt ou .onnx.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Confianca minima para exibir deteccoes.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
        help="Resolucao usada na inferencia.",
    )
    parser.add_argument(
        "--detectar-a-cada",
        type=int,
        default=2,
        help="Executa inferencia a cada N frames.",
    )
    parser.add_argument(
        "--roi",
        default=None,
        help=(
            "Regiao normalizada x,y,largura,altura. "
            "Ex.: 0,0,0.55,1"
        ),
    )
    parser.add_argument(
        "--suavizacao",
        type=float,
        default=0.65,
        help=(
            "Suavizacao da caixa entre 0 e 1. "
            "1 desativa suavizacao."
        ),
    )
    parser.add_argument(
        "--tolerar-falhas",
        type=int,
        default=2,
        help=(
            "Mantem a ultima deteccao por N falhas "
            "consecutivas. Padrao: 2."
        ),
    )
    args = parser.parse_args()

    try:
        roi = parse_roi(args.roi)
        detector = DetectorPlayer(
            modelo=args.modelo,
            conf=args.conf,
            imgsz=args.imgsz,
            roi=roi,
            suavizacao=args.suavizacao,
        )
    except (FileNotFoundError, ValueError) as erro:
        print(erro)
        return

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    detectar_a_cada = max(1, args.detectar_a_cada)

    try:
        memoria = MemoriaDeteccao(
            max_falhas=args.tolerar_falhas,
        )
    except ValueError as erro:
        print(erro)
        return

    print("Detector ao vivo iniciado.")
    print(f"Modelo: {args.modelo}")
    print(
        f"Inferencia: imgsz={args.imgsz}, "
        f"a cada {detectar_a_cada} frame(s)"
    )
    print(
        "Tolerancia temporal: "
        f"{args.tolerar_falhas} falha(s)"
    )

    if roi is not None:
        print(f"ROI ativa: {args.roi}")

    print("Q = encerrar")

    contador_frames = 0
    ultima_caixa = None
    ultima_confianca = 0.0
    ultima_inferencia_ms = 0.0
    em_memoria = False
    fps = 0.0
    ultimo_frame_tempo = time.perf_counter()

    try:
        while True:
            try:
                frame = captura.capturar()
            except (
                IdleSlayerNaoEncontrado,
                CapturaIndisponivel,
            ) as erro:
                print(f"Captura encerrada: {erro}")
                break

            contador_frames += 1

            agora = time.perf_counter()
            delta = agora - ultimo_frame_tempo
            ultimo_frame_tempo = agora

            if delta > 0:
                fps_instantaneo = 1.0 / delta
                fps = (
                    fps_instantaneo
                    if fps == 0
                    else fps * 0.9
                    + fps_instantaneo * 0.1
                )

            if contador_frames % detectar_a_cada == 0:
                deteccao_bruta = detector.detectar(frame)
                deteccao = memoria.atualizar(
                    deteccao_bruta
                )
                em_memoria = (
                    deteccao_bruta is None
                    and deteccao is not None
                )

                if deteccao is None:
                    ultima_caixa = None
                    ultima_confianca = 0.0
                    em_memoria = False
                else:
                    ultima_caixa = deteccao.caixa
                    ultima_confianca = deteccao.confianca

                    if deteccao_bruta is not None:
                        ultima_inferencia_ms = (
                            deteccao.inferencia_ms
                        )

            preview = frame.copy()

            if roi is not None:
                x1r, y1r, x2r, y2r = calcular_roi_pixels(
                    frame.shape[1],
                    frame.shape[0],
                    roi,
                )
                cv2.rectangle(
                    preview,
                    (x1r, y1r),
                    (x2r, y2r),
                    (255, 255, 0),
                    1,
                )

            if ultima_caixa is not None:
                x1, y1, x2, y2 = ultima_caixa
                cor = (
                    (0, 215, 255)
                    if em_memoria
                    else (0, 255, 0)
                )
                rotulo = (
                    f"player {ultima_confianca:.2f} memoria"
                    if em_memoria
                    else f"player {ultima_confianca:.2f}"
                )

                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    cor,
                    2,
                )

                cv2.putText(
                    preview,
                    rotulo,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    cor,
                    2,
                    cv2.LINE_AA,
                )

            cv2.putText(
                preview,
                (
                    f"FPS {fps:.1f} | "
                    f"inferencia {ultima_inferencia_ms:.0f} ms"
                ),
                (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "SlayerAI - Detector ao vivo",
                preview,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        captura.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
