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
    print("Q = encerrar")

    try:
        while True:
            try:
                frame = captura.capturar()
            except (IdleSlayerNaoEncontrado, CapturaIndisponivel) as erro:
                print(f"Captura encerrada: {erro}")
                break

            resultados = modelo.predict(
                source=frame,
                conf=args.conf,
                verbose=False,
            )

            preview = frame.copy()

            if resultados:
                caixas = resultados[0].boxes

                for caixa in caixas:
                    x1, y1, x2, y2 = (
                        caixa.xyxy[0]
                        .cpu()
                        .numpy()
                        .astype(int)
                        .tolist()
                    )
                    confianca = float(caixa.conf[0].item())

                    cv2.rectangle(
                        preview,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        preview,
                        f"player {confianca:.2f}",
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
