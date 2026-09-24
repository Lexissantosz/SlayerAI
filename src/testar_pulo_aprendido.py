import argparse
import time
from pathlib import Path

import cv2

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from modelo_pulo import (
    carregar_dataset_modelo,
    criar_knn,
    extrair_caracteristicas,
    prever,
)


ROOT = Path(__file__).resolve().parent.parent
MODELO = ROOT / "modelos/pulo_demo_v01.npz"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Testa ao vivo o primeiro modelo de "
            "imitacao do pulo, sem enviar teclas."
        )
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO),
    )
    parser.add_argument(
        "--limiar",
        type=float,
        default=0.80,
        help=(
            "Probabilidade minima para mostrar PULAR. "
            "Padrao: 0.80."
        ),
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=8.0,
    )
    args = parser.parse_args()

    if not 0 < args.limiar <= 1:
        raise ValueError(
            "--limiar deve estar entre 0 e 1."
        )

    amostras, rotulos = (
        carregar_dataset_modelo(
            args.modelo
        )
    )
    knn = criar_knn(
        amostras,
        rotulos,
    )

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    intervalo = 1.0 / max(
        args.fps,
        1.0,
    )

    print("SlayerAI - Pulo aprendido (dry-run)")
    print("=" * 40)
    print(f"Modelo: {args.modelo}")
    print(
        f"Limiar de pulo: {args.limiar:.2f}"
    )
    print(
        "Nenhuma tecla sera enviada. Q encerra."
    )

    try:
        while True:
            inicio = time.perf_counter()

            try:
                frame = captura.capturar()
            except (
                IdleSlayerNaoEncontrado,
                CapturaIndisponivel,
            ) as erro:
                print(
                    f"Captura encerrada: {erro}"
                )
                break

            caracteristicas = (
                extrair_caracteristicas(frame)
            )
            _, prob = prever(
                knn,
                caracteristicas,
            )

            quer_pular = (
                prob >= args.limiar
            )

            preview = frame.copy()
            texto = (
                f"PULO {prob:.0%} | "
                + (
                    "PULAR"
                    if quer_pular
                    else "esperar"
                )
            )

            cv2.rectangle(
                preview,
                (0, 0),
                (
                    preview.shape[1],
                    48,
                ),
                (0, 0, 0),
                -1,
            )
            cv2.putText(
                preview,
                texto,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "SlayerAI - Pulo aprendido",
                preview,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

            gasto = (
                time.perf_counter()
                - inicio
            )
            restante = (
                intervalo - gasto
            )

            if restante > 0:
                time.sleep(restante)

    finally:
        captura.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
