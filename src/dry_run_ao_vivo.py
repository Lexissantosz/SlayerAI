import argparse
from pathlib import Path

import cv2

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from decisor import Decisao, DecisorBasico
from detector import DetectorPlayer
from executor import ExecutorAcoes
from memoria_deteccao import MemoriaDeteccao
from pipeline import CicloSlayerAI
from registro_sessao import GravadorSessao
from visao_utils import calcular_roi_pixels, parse_roi


ROOT = Path(__file__).resolve().parent.parent
MODELO = ROOT / "modelos/player_v01.onnx"


class ExecutorDryRun(ExecutorAcoes):
    def __init__(self) -> None:
        self.ultima: Decisao | None = None

    def executar(self, decisao: Decisao) -> None:
        if self.ultima != decisao:
            print(
                f"[DRY-RUN] {decisao.acao.value}: "
                f"{decisao.motivo}"
            )
            self.ultima = decisao


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Liga captura + detector real + EstadoJogo + "
            "decisor sem enviar teclas."
        )
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.30,
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=320,
    )
    parser.add_argument(
        "--detectar-a-cada",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--roi",
        default="0,0,0.30,1",
    )
    parser.add_argument(
        "--tolerar-falhas",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--player-max-x",
        type=float,
        default=0.14,
        help=(
            "Centro X maximo esperado do player, "
            "normalizado pela largura da tela. Padrao: 0.14."
        ),
    )
    parser.add_argument(
        "--saida",
        default="sessoes/live_dry_run.jsonl",
    )
    args = parser.parse_args()

    try:
        roi = parse_roi(args.roi)
        detector = DetectorPlayer(
            modelo=MODELO,
            conf=args.conf,
            imgsz=args.imgsz,
            roi=roi,
            suavizacao=0.65,
        )
        memoria = MemoriaDeteccao(
            max_falhas=args.tolerar_falhas,
            max_centro_x=args.player_max_x,
        )
    except (FileNotFoundError, ValueError) as erro:
        print(erro)
        return

    try:
        captura = IdleSlayerCapture()
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    executor = ExecutorDryRun()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )
    gravador = GravadorSessao(args.saida)

    detectar_a_cada = max(1, args.detectar_a_cada)
    contador_frames = 0
    ultima_deteccao = None
    ultima_decisao = None
    em_memoria = False

    print("SlayerAI - dry-run ao vivo")
    print("Nenhuma tecla sera enviada.")
    print(
        f"conf={args.conf} | imgsz={args.imgsz} | "
        f"ROI={args.roi} | "
        f"tolerancia={args.tolerar_falhas} | "
        f"player_max_x={args.player_max_x:.2f}"
    )
    print("Q = encerrar")

    try:
        while True:
            try:
                frame = captura.capturar()
            except (
                IdleSlayerNaoEncontrado,
                CapturaIndisponivel,
            ) as erro:
                print(f"Captura encerrada: {erro}")
                break

            contador_frames += 1

            if contador_frames % detectar_a_cada == 0:
                bruta = detector.detectar(frame)
                ultima_deteccao = memoria.atualizar(
                    bruta,
                    largura_frame=frame.shape[1],
                )
                em_memoria = (
                    (
                        bruta is None
                        or memoria.ultima_rejeitada
                    )
                    and ultima_deteccao is not None
                )

                resultado = ciclo.processar(
                    largura=frame.shape[1],
                    altura=frame.shape[0],
                    deteccao_player=ultima_deteccao,
                )
                ultima_decisao = resultado.decisao

                gravador.registrar(
                    frame=contador_frames,
                    estado=resultado.estado,
                    decisao=resultado.decisao,
                )

            preview = frame.copy()

            if roi is not None:
                x1r, y1r, x2r, y2r = calcular_roi_pixels(
                    frame.shape[1],
                    frame.shape[0],
                    roi,
                )
                cv2.rectangle(
                    preview,
                    (x1r, y1r),
                    (x2r, y2r),
                    (255, 255, 0),
                    1,
                )

            if ultima_deteccao is not None:
                x1, y1, x2, y2 = ultima_deteccao.caixa
                cor = (
                    (0, 215, 255)
                    if em_memoria
                    else (0, 255, 0)
                )
                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    cor,
                    2,
                )

            decisao_texto = (
                ultima_decisao.acao.value
                if ultima_decisao is not None
                else "aguardando"
            )
            cv2.putText(
                preview,
                f"DRY-RUN | decisao: {decisao_texto}",
                (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "SlayerAI - Dry-run ao vivo",
                preview,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        captura.close()
        cv2.destroyAllWindows()

    print(f"Sessao salva em: {args.saida}")


if __name__ == "__main__":
    main()
