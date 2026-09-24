import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
DATASET_YAML = ROOT / "dataset_v02.yaml"
TRAIN_IMAGES = ROOT / "dataset_v02/train/images"
VAL_IMAGES = ROOT / "dataset_v02/val/images"
MODELOS_DIR = ROOT / "modelos"
RUNS_DIR = ROOT / "runs/slayerai"


def contar_imagens(pasta: Path) -> int:
    return sum(1 for _ in pasta.glob("*.png"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Treina o detector multiclasse v0.2 "
            "(player + inimigo)."
        )
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Quantidade de epocas. Padrao: 30.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
        help="Resolucao usada no treino. Padrao: 320.",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=4,
        help="Tamanho do batch. Padrao: 4.",
    )
    parser.add_argument(
        "--modelo",
        default="yolo11n.pt",
        help="Modelo base do Ultralytics.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help='Dispositivo, por exemplo "cpu" ou "0".',
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=8,
        help=(
            "Epocas sem melhora antes de early stopping. "
            "Padrao: 8."
        ),
    )
    parser.add_argument(
        "--nome-run",
        default="multiclasse_v02",
        help=(
            "Nome da pasta do run. "
            "Padrao: multiclasse_v02."
        ),
    )
    parser.add_argument(
        "--saida-modelo",
        default="multiclasse_v02_best.pt",
        help=(
            "Nome do melhor peso copiado para modelos/. "
            "Padrao: multiclasse_v02_best.pt."
        ),
    )
    args = parser.parse_args()

    treino = contar_imagens(TRAIN_IMAGES)
    validacao = contar_imagens(VAL_IMAGES)

    if treino == 0 or validacao == 0:
        print("Dataset v0.2 ainda nao foi dividido.")
        print(
            "Rode primeiro: "
            "python src/preparar_dataset_v02.py "
            "--val-prefixo frame"
        )
        return

    if not DATASET_YAML.exists():
        print(
            f"Configuracao do dataset nao encontrada: "
            f"{DATASET_YAML}"
        )
        return

    print("SlayerAI - Treino detector v0.2")
    print("=" * 40)
    print(f"Imagens de treino: {treino}")
    print(f"Imagens de validacao: {validacao}")
    print(f"Modelo base: {args.modelo}")
    print(f"Device: {args.device}")
    print(f"Epochs: {args.epochs}")
    print(f"imgsz: {args.imgsz}")
    print(f"batch: {args.batch}")
    print("Iniciando treino...")

    modelo = YOLO(args.modelo)

    resultado = modelo.train(
        data=str(DATASET_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str(RUNS_DIR),
        name=args.nome_run,
        exist_ok=True,
        workers=0,
        seed=42,
        plots=True,
        verbose=True,
        patience=args.patience,
    )

    save_dir = Path(resultado.save_dir)
    melhor_peso = save_dir / "weights" / "best.pt"

    if not melhor_peso.exists():
        print("")
        print(
            "Treino terminou, mas best.pt nao foi encontrado."
        )
        print(f"Confira: {save_dir}")
        return

    MODELOS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    destino = (
        MODELOS_DIR
        / args.saida_modelo
    )
    shutil.copy2(
        melhor_peso,
        destino,
    )

    print("")
    print("Treino concluido.")
    print(f"Melhor modelo: {destino}")
    print(
        f"Resultados completos: {save_dir}"
    )
    print("")
    print(
        "Proximo passo: testar o modelo .pt ao vivo "
        "antes da exportacao ONNX."
    )


if __name__ == "__main__":
    main()
