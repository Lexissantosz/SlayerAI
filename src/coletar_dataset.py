import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)


PASTA_RAW = Path("dataset/raw")


def assinatura(frame: np.ndarray) -> np.ndarray:
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.resize(cinza, (64, 36), interpolation=cv2.INTER_AREA)


def diferenca_percentual(
    atual: np.ndarray,
    anterior: np.ndarray,
) -> float:
    diferenca = cv2.absdiff(atual, anterior)
    return float(diferenca.mean() / 255.0 * 100.0)


def salvar_frame(frame: np.ndarray, indice: int) -> Path:
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho = PASTA_RAW / f"frame_{indice:05d}_{momento}.png"
    cv2.imwrite(str(caminho), frame)
    return caminho


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Coleta frames variados do Idle Slayer para o dataset."
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=0.20,
        help="Intervalo minimo entre frames salvos, em segundos.",
    )
    parser.add_argument(
        "--mudanca-minima",
        type=float,
        default=1.0,
        help="Mudanca visual minima em %% para salvar outro frame.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=300,
        help="Numero maximo de frames. Use 0 para ilimitado.",
    )
    args = parser.parse_args()

    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    print("Coleta iniciada.")
    print("Q = encerrar | S = salvar um frame imediatamente")

    ultimo_salvo = 0.0
    assinatura_anterior = None
    salvos = 0

    try:
        while True:
            try:
                frame = captura.capturar()
            except (IdleSlayerNaoEncontrado, CapturaIndisponivel) as erro:
                print(f"Captura encerrada: {erro}")
                break

            agora = time.monotonic()
            atual = assinatura(frame)
            pode_salvar = agora - ultimo_salvo >= args.intervalo

            mudanca = 100.0
            if assinatura_anterior is not None:
                mudanca = diferenca_percentual(
                    atual,
                    assinatura_anterior,
                )

            preview = frame.copy()
            cv2.putText(
                preview,
                f"Salvos: {salvos} | Mudanca: {mudanca:.2f}%",
                (12, 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("SlayerAI - Coleta de dataset", preview)

            tecla = cv2.waitKey(1) & 0xFF
            forcar = tecla == ord("s")

            if forcar or (
                pode_salvar
                and (
                    assinatura_anterior is None
                    or mudanca >= args.mudanca_minima
                )
            ):
                caminho = salvar_frame(frame, salvos)
                salvos += 1
                ultimo_salvo = agora
                assinatura_anterior = atual.copy()
                print(f"[{salvos}] {caminho}")

            if tecla == ord("q"):
                break

            if args.limite > 0 and salvos >= args.limite:
                print("Limite de frames atingido.")
                break

    finally:
        captura.close()
        cv2.destroyAllWindows()

    print(f"Coleta finalizada com {salvos} frame(s).")


if __name__ == "__main__":
    main()
