import argparse
import time
from pathlib import Path

import cv2

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from detector_multiclasse import (
    DetectorMulticlasse,
)
from estado_jogo import TipoObjeto


ROOT = Path(__file__).resolve().parent.parent
MODELO_ONNX = (
    ROOT
    / "modelos/multiclasse_v02.onnx"
)
MODELO_PT = (
    ROOT
    / "modelos/multiclasse_v02_best.pt"
)
MODELO_PADRAO = (
    MODELO_ONNX
    if MODELO_ONNX.exists()
    else MODELO_PT
)

CORES = {
    TipoObjeto.PLAYER: (0, 255, 0),
    TipoObjeto.INIMIGO: (0, 0, 255),
    TipoObjeto.DESCONHECIDO: (0, 255, 255),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Testa o detector multiclasse v0.2 "
            "ao vivo."
        )
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO_PADRAO),
        help="Caminho do modelo .pt ou .onnx.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.30,
        help="Confianca minima. Padrao: 0.30.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
        help="Resolucao da inferencia. Padrao: 320.",
    )
    parser.add_argument(
        "--detectar-a-cada",
        type=int,
        default=2,
        help=(
            "Executa inferencia a cada N frames. "
            "Padrao: 2."
        ),
    )
    args = parser.parse_args()

    try:
        detector = DetectorMulticlasse(
            modelo=args.modelo,
            conf=args.conf,
            imgsz=args.imgsz,
        )
    except (
        FileNotFoundError,
        ValueError,
    ) as erro:
        print(erro)
        return

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    detectar_a_cada = max(
        1,
        args.detectar_a_cada,
    )

    print(
        "Detector multiclasse v0.2 iniciado."
    )
    print(f"Modelo: {args.modelo}")
    print(
        f"Inferencia: imgsz={args.imgsz}, "
        f"a cada {detectar_a_cada} frame(s)"
    )
    print("Q = encerrar")

    contador_frames = 0
    ultima_deteccoes = []
    ultima_inferencia_ms = 0.0
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
                print(
                    f"Captura encerrada: {erro}"
                )
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

            if (
                contador_frames
                % detectar_a_cada
                == 0
            ):
                resultado = detector.detectar(
                    frame
                )
                ultima_deteccoes = (
                    resultado.deteccoes
                )
                ultima_inferencia_ms = (
                    resultado.inferencia_ms
                )

            preview = frame.copy()
            contagem = {
                TipoObjeto.PLAYER: 0,
                TipoObjeto.INIMIGO: 0,
            }

            for deteccao in ultima_deteccoes:
                x1, y1, x2, y2 = (
                    deteccao.caixa
                )
                cor = CORES.get(
                    deteccao.tipo,
                    (255, 255, 255),
                )

                if deteccao.tipo in contagem:
                    contagem[deteccao.tipo] += 1

                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    cor,
                    2,
                )

                rotulo = (
                    f"{deteccao.tipo.value} "
                    f"{deteccao.confianca:.2f}"
                )
                cv2.putText(
                    preview,
                    rotulo,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    cor,
                    2,
                    cv2.LINE_AA,
                )

            texto = (
                f"FPS {fps:.1f} | "
                f"inferencia "
                f"{ultima_inferencia_ms:.0f} ms | "
                f"player {contagem[TipoObjeto.PLAYER]} | "
                f"inimigos "
                f"{contagem[TipoObjeto.INIMIGO]}"
            )
            cv2.putText(
                preview,
                texto,
                (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "SlayerAI - Detector v0.2",
                preview,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:
        captura.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
