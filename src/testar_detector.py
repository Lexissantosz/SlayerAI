import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)


ROOT = Path(__file__).resolve().parent.parent
MODELO_PADRAO = ROOT / "modelos/player_v01_best.pt"


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
        help="Resolucao usada na inferencia. 320 tende a ser bem mais rapido em CPU.",
    )
    parser.add_argument(
        "--detectar-a-cada",
        type=int,
        default=2,
        help="Executa inferencia a cada N frames e reutiliza a ultima caixa entre eles.",
    )
    args = parser.parse_args()

    caminho_modelo = Path(args.modelo)

    if not caminho_modelo.exists():
        print(f"Modelo nao encontrado: {caminho_modelo}")
        print("Treine primeiro com: python src/treinar_detector.py")
        return

    modelo = YOLO(str(caminho_modelo))

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    print("Detector ao vivo iniciado.")
    print(
        f"Inferencia: imgsz={args.imgsz}, "
        f"a cada {args.detectar_a_cada} frame(s)"
    )
    print("Q = encerrar")

    contador_frames = 0
    ultima_caixa = None
    ultima_confianca = 0.0

    try:
        while True:
            try:
                frame = captura.capturar()
            except (IdleSlayerNaoEncontrado, CapturaIndisponivel) as erro:
                print(f"Captura encerrada: {erro}")
                break

            contador_frames += 1

            if contador_frames % max(1, args.detectar_a_cada) == 0:
                resultados = modelo.predict(
                    source=frame,
                    conf=args.conf,
                    imgsz=args.imgsz,
                    verbose=False,
                    device="cpu",
                )

                ultima_caixa = None
                ultima_confianca = 0.0

                if resultados and len(resultados[0].boxes) > 0:
                    melhor = max(
                        resultados[0].boxes,
                        key=lambda caixa: float(caixa.conf[0].item()),
                    )

                    ultima_caixa = (
                        melhor.xyxy[0]
                        .cpu()
                        .numpy()
                        .astype(int)
                        .tolist()
                    )
                    ultima_confianca = float(
                        melhor.conf[0].item()
                    )

            preview = frame.copy()

            if ultima_caixa is not None:
                x1, y1, x2, y2 = ultima_caixa

                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    preview,
                    f"player {ultima_confianca:.2f}",
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
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
