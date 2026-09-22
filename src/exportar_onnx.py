from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
MODELO_PT = ROOT / "modelos/player_v01_best.pt"
MODELOS_DIR = ROOT / "modelos"


def main() -> None:
    if not MODELO_PT.exists():
        print(f"Modelo nao encontrado: {MODELO_PT}")
        print("Treine primeiro o detector.")
        return

    print("Exportando modelo para ONNX...")
    print("Configuracao focada em CPU e portabilidade.")

    modelo = YOLO(str(MODELO_PT))

    resultado = modelo.export(
        format="onnx",
        imgsz=320,
        simplify=True,
        dynamic=False,
        opset=12,
    )

    origem = Path(resultado)
    destino = MODELOS_DIR / "player_v01.onnx"

    if origem.resolve() != destino.resolve():
        destino.write_bytes(origem.read_bytes())

    print("")
    print("Exportacao concluida.")
    print(f"Modelo ONNX: {destino}")
    print("")
    print("Teste com:")
    print(
        "python src/testar_detector.py "
        "--modelo modelos/player_v01.onnx "
        "--imgsz 320 --detectar-a-cada 2"
    )


if __name__ == "__main__":
    main()
