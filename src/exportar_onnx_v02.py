from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
MODELO_PT = (
    ROOT
    / "modelos/multiclasse_v02_best.pt"
)
MODELOS_DIR = ROOT / "modelos"


def main() -> None:
    if not MODELO_PT.exists():
        print(
            f"Modelo nao encontrado: {MODELO_PT}"
        )
        print(
            "Treine primeiro o detector v0.2."
        )
        return

    print(
        "Exportando detector multiclasse v0.2 "
        "para ONNX..."
    )
    print(
        "Configuracao focada em CPU e portabilidade."
    )

    modelo = YOLO(str(MODELO_PT))

    resultado = modelo.export(
        format="onnx",
        imgsz=320,
        simplify=True,
        dynamic=False,
        opset=12,
    )

    origem = Path(resultado)
    destino = (
        MODELOS_DIR
        / "multiclasse_v02.onnx"
    )

    if origem.resolve() != destino.resolve():
        destino.write_bytes(
            origem.read_bytes()
        )

    print("")
    print("Exportacao concluida.")
    print(f"Modelo ONNX: {destino}")
    print("")
    print("Teste com:")
    print(
        "python src/testar_detector_v02.py "
        "--modelo modelos/multiclasse_v02.onnx"
    )


if __name__ == "__main__":
    main()
