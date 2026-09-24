import argparse
from pathlib import Path

import cv2

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from decisor import DecisorBasico
from detector_multiclasse import (
    DetectorMulticlasse,
)
from executor import ExecutorSimulado
from pipeline import CicloSlayerAI
from registro_sessao import GravadorSessao


ROOT = Path(__file__).resolve().parent.parent
MODELO_ONNX = (
    ROOT
    / "modelos/multiclasse_v02.onnx"
)
MODELO_PT = (
    ROOT
    / "modelos/multiclasse_v02_best.pt"
)
MODELO_PADRAO = (
    MODELO_ONNX
    if MODELO_ONNX.exists()
    else MODELO_PT
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Executa detector multiclasse + EstadoJogo "
            "+ decisor sem enviar comandos ao jogo."
        )
    )
    parser.add_argument(
        "--modelo",
        default=str(MODELO_PADRAO),
        help="Modelo .pt ou .onnx da v0.2.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.30,
        help="Confianca minima. Padrao: 0.30.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
        help="Resolucao da inferencia. Padrao: 320.",
    )
    parser.add_argument(
        "--detectar-a-cada",
        type=int,
        default=2,
        help=(
            "Executa inferencia a cada N frames. "
            "Padrao: 2."
        ),
    )
    parser.add_argument(
        "--saida",
        default="sessoes/dry_run_v02.jsonl",
        help=(
            "Arquivo JSONL da sessao. "
            "Padrao: sessoes/dry_run_v02.jsonl"
        ),
    )
    args = parser.parse_args()

    try:
        detector = DetectorMulticlasse(
            modelo=args.modelo,
            conf=args.conf,
            imgsz=args.imgsz,
        )
    except (
        FileNotFoundError,
        ValueError,
    ) as erro:
        print(erro)
        return

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        decisor=DecisorBasico(),
        executor=executor,
    )
    gravador = GravadorSessao(args.saida)

    detectar_a_cada = max(
        1,
        args.detectar_a_cada,
    )

    print("SlayerAI - Dry-run real v0.2")
    print("=" * 40)
    print(
        "MODO SEGURO: nenhuma tecla sera enviada."
    )
    print(f"Modelo: {args.modelo}")
    print(f"Sessao: {args.saida}")
    print("Q = encerrar")

    frame_id = 0
    ultima_deteccoes = []
    ultima_inferencia_ms = 0.0

    try:
        while True:
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

            frame_id += 1

            if (
                frame_id
                % detectar_a_cada
                == 0
            ):
                resultado_visao = (
                    detector.detectar(frame)
                )
                ultima_deteccoes = (
                    resultado_visao.deteccoes
                )
                ultima_inferencia_ms = (
                    resultado_visao.inferencia_ms
                )

                resultado = (
                    ciclo.processar_deteccoes(
                        largura=frame.shape[1],
                        altura=frame.shape[0],
                        deteccoes=ultima_deteccoes,
                    )
                )

                gravador.registrar(
                    frame=frame_id,
                    estado=resultado.estado,
                    decisao=resultado.decisao,
                )

            preview = frame.copy()

            for deteccao in ultima_deteccoes:
                x1, y1, x2, y2 = deteccao.caixa

                cor = (
                    (0, 255, 0)
                    if deteccao.tipo.value
                    == "player"
                    else (0, 0, 255)
                )

                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    cor,
                    2,
                )

            cv2.putText(
                preview,
                (
                    "DRY-RUN | "
                    f"{ultima_inferencia_ms:.0f} ms"
                ),
                (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "SlayerAI - Dry-run real v0.2",
                preview,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:
        captura.close()
        cv2.destroyAllWindows()

    print("")
    print(
        f"Sessao salva em: {args.saida}"
    )
    print(
        "Nenhum comando real foi enviado ao jogo."
    )


if __name__ == "__main__":
    main()
