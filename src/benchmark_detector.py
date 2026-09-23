import argparse
import statistics
from pathlib import Path

import cv2

from detector import DetectorPlayer
from visao_utils import parse_roi


ROOT = Path(__file__).resolve().parent.parent
MODELO_ONNX = ROOT / "modelos/player_v01.onnx"
MODELO_PT = ROOT / "modelos/player_v01_best.pt"
MODELO_PADRAO = MODELO_ONNX if MODELO_ONNX.exists() else MODELO_PT
RAW_DIR = ROOT / "dataset/raw"


def percentil(valores: list[float], fracao: float) -> float:
    ordenados = sorted(valores)

    if not ordenados:
        return 0.0

    indice = round((len(ordenados) - 1) * fracao)
    return ordenados[indice]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mede desempenho do detector em frames salvos."
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO_PADRAO),
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--roi",
        default=None,
        help="ROI normalizada x,y,largura,altura. Ex.: 0,0,0.5,1",
    )
    args = parser.parse_args()

    roi = parse_roi(args.roi)

    detector = DetectorPlayer(
        modelo=args.modelo,
        conf=args.conf,
        imgsz=args.imgsz,
        roi=roi,
        suavizacao=1.0,
    )

    imagens = sorted(RAW_DIR.glob("*.png"))

    if args.limite > 0:
        imagens = imagens[: args.limite]

    if not imagens:
        print("Nenhum frame encontrado em dataset/raw.")
        return

    tempos = []
    confiancas = []
    detectadas = 0
    processadas = 0

    for caminho in imagens:
        frame = cv2.imread(str(caminho))

        if frame is None:
            continue

        processadas += 1
        deteccao = detector.detectar(frame)

        if deteccao is None:
            continue

        detectadas += 1
        tempos.append(deteccao.inferencia_ms)
        confiancas.append(deteccao.confianca)

    if processadas == 0:
        print("Nenhuma imagem valida foi processada.")
        return

    taxa = detectadas / processadas * 100.0

    print(f"Modelo: {args.modelo}")
    print(f"Imagens processadas: {processadas}")
    print(f"Deteccoes: {detectadas} ({taxa:.1f}%)")

    if tempos:
        print(f"Inferencia media: {statistics.mean(tempos):.1f} ms")
        print(f"Mediana: {statistics.median(tempos):.1f} ms")
        print(f"P95: {percentil(tempos, 0.95):.1f} ms")
        print(
            f"Confianca media: "
            f"{statistics.mean(confiancas):.3f}"
        )


if __name__ == "__main__":
    main()
