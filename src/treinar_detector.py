import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
DATASET_YAML = ROOT / "dataset.yaml"
TRAIN_IMAGES = ROOT / "dataset/train/images"
VAL_IMAGES = ROOT / "dataset/val/images"
MODELOS_DIR = ROOT / "modelos"
RUNS_DIR = ROOT / "runs/slayerai"


def contar_imagens(pasta: Path) -> int:
    return sum(1 for _ in pasta.glob("*.png"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Treina o primeiro detector do personagem do SlayerAI."
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=40,
        help="Quantidade de epocas de treino.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamanho da imagem usado pelo YOLO.",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=8,
        help="Tamanho do batch. Reduza se faltar memoria.",
    )
    parser.add_argument(
        "--modelo",
        default="yolo11n.pt",
        help="Modelo base do Ultralytics.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help='Dispositivo do treino, por exemplo "cpu" ou "0".',
    )
    args = parser.parse_args()

    treino = contar_imagens(TRAIN_IMAGES)
    validacao = contar_imagens(VAL_IMAGES)

    if treino == 0 or validacao == 0:
        print("Dataset ainda nao foi dividido.")
        print("Rode primeiro: python src/preparar_dataset.py")
        return

    print(f"Imagens de treino: {treino}")
    print(f"Imagens de validacao: {validacao}")
    print(f"Modelo base: {args.modelo}")
    print("Iniciando treino...")

    modelo = YOLO(args.modelo)

    kwargs = {
        "data": str(DATASET_YAML),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "project": str(RUNS_DIR),
        "name": "player_v01",
        "exist_ok": True,
        "workers": 0,
        "seed": 42,
        "plots": True,
        "verbose": True,
    }

    if args.device:
        kwargs["device"] = args.device

    resultado = modelo.train(**kwargs)

    save_dir = Path(resultado.save_dir)
    melhor_peso = save_dir / "weights" / "best.pt"

    if not melhor_peso.exists():
        print("Treino terminou, mas best.pt nao foi encontrado.")
        print(f"Confira: {save_dir}")
        return

    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    destino = MODELOS_DIR / "player_v01_best.pt"
    shutil.copy2(melhor_peso, destino)

    print("")
    print("Treino concluido.")
    print(f"Melhor modelo: {destino}")
    print(f"Resultados completos: {save_dir}")
    print("")
    print("Proximo passo: testar o detector ao vivo antes de exportar para ONNX.")


if __name__ == "__main__":
    main()
