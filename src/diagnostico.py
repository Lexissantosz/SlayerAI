import importlib.metadata
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def versao_pacote(nome: str) -> str:
    try:
        return importlib.metadata.version(nome)
    except importlib.metadata.PackageNotFoundError:
        return "NAO INSTALADO"


def existe(caminho: Path) -> str:
    return "OK" if caminho.exists() else "AUSENTE"


def main() -> None:
    print("SlayerAI - Diagnostico")
    print("=" * 40)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print("")

    print("Dependencias:")
    for pacote in (
        "numpy",
        "opencv-python",
        "pywin32",
        "ultralytics",
        "onnx",
        "onnxruntime",
        "polars",
    ):
        print(f"- {pacote}: {versao_pacote(pacote)}")

    print("")
    print("Arquivos:")
    caminhos = (
        ROOT / "modelos/player_v01.onnx",
        ROOT / "modelos/player_v01_best.pt",
        ROOT / "dataset.yaml",
    )

    for caminho in caminhos:
        print(
            f"- {caminho.relative_to(ROOT)}: "
            f"{existe(caminho)}"
        )

    print("")
    print("Janela do jogo:")

    try:
        import win32gui

        hwnd = win32gui.FindWindow(None, "Idle Slayer")

        if hwnd:
            print(
                "- Idle Slayer: ENCONTRADO "
                f"(handle {hwnd})"
            )
        else:
            print("- Idle Slayer: NAO ENCONTRADO")
    except Exception as erro:
        print(f"- Nao foi possivel verificar: {erro}")


if __name__ == "__main__":
    main()
