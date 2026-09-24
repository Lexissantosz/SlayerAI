import argparse
from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
DATASET_YAML = ROOT / "dataset_v02.yaml"
MODELO_PT = (
    ROOT
    / "modelos/multiclasse_v02_best.pt"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Avalia o detector multiclasse v0.2 "
            "no conjunto de validacao."
        )
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO_PT),
        help="Caminho do modelo .pt ou .onnx.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
        help="Resolucao da avaliacao. Padrao: 320.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help='Dispositivo, por exemplo "cpu" ou "0".',
    )
    args = parser.parse_args()

    caminho_modelo = Path(args.modelo)

    if not caminho_modelo.exists():
        print(
            f"Modelo nao encontrado: {caminho_modelo}"
        )
        return

    if not DATASET_YAML.exists():
        print(
            "dataset_v02.yaml nao encontrado."
        )
        return

    print("SlayerAI - Avaliacao detector v0.2")
    print("=" * 40)
    print(f"Modelo: {caminho_modelo}")
    print(f"imgsz: {args.imgsz}")
    print(f"device: {args.device}")

    modelo = YOLO(str(caminho_modelo))

    metricas = modelo.val(
        data=str(DATASET_YAML),
        split="val",
        imgsz=args.imgsz,
        device=args.device,
        workers=0,
        plots=True,
        verbose=True,
    )

    print("")
    print("Resumo:")
    print(
        f"mAP50-95: {metricas.box.map:.4f}"
    )
    print(
        f"mAP50: {metricas.box.map50:.4f}"
    )
    print(
        f"mAP75: {metricas.box.map75:.4f}"
    )

    mapas = list(metricas.box.maps)

    for classe_id, valor in enumerate(mapas):
        nome = metricas.names.get(
            classe_id,
            f"classe_{classe_id}",
        )
        print(
            f"mAP50-95 {nome}: {float(valor):.4f}"
        )


if __name__ == "__main__":
    main()
