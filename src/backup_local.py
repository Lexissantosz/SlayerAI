import argparse
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

PASTAS_PADRAO = (
    ROOT / "dataset",
    ROOT / "modelos",
    ROOT / "assets",
    ROOT / "capturas",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cria um ZIP com artefatos locais que ficam fora do GitHub, "
            "como dataset, modelos e assets."
        )
    )
    parser.add_argument(
        "--destino",
        default=str(ROOT / "backups"),
        help="Pasta onde o ZIP sera salvo.",
    )
    args = parser.parse_args()

    destino = Path(args.destino)
    destino.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_zip = destino / f"slayerai_local_{timestamp}"

    staging = destino / f".tmp_slayerai_{timestamp}"
    staging.mkdir(parents=True, exist_ok=True)

    copiados = 0

    try:
        for pasta in PASTAS_PADRAO:
            if not pasta.exists():
                continue

            destino_pasta = staging / pasta.name
            shutil.copytree(
                pasta,
                destino_pasta,
                dirs_exist_ok=True,
            )
            copiados += 1

        if copiados == 0:
            print("Nenhum artefato local encontrado para backup.")
            return

        arquivo = shutil.make_archive(
            str(base_zip),
            "zip",
            root_dir=staging,
        )

        print("Backup local criado:")
        print(arquivo)
        print("")
        print(
            "Guarde esse ZIP fora do PC "
            "(Drive, pendrive, HD externo, etc.)."
        )
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    main()
