import argparse
import json
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import win32api
import win32con

from captura import (
    CapturaIndisponivel,
    IdleSlayerCapture,
    IdleSlayerNaoEncontrado,
)
from configuracao import carregar_configuracao_controles
from decisor import Acao


ACOES_OBSERVADAS = (
    Acao.PULAR,
    Acao.ATACAR,
    Acao.ATIRAR,
)


def tecla_pressionada(codigo: int) -> bool:
    return bool(
        win32api.GetAsyncKeyState(codigo)
        & 0x8000
    )


def nome_sessao() -> str:
    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


def salvar_evento(
    pasta_sessao: Path,
    indice: int,
    evento: dict,
) -> dict:
    nome = (
        f"evento_{indice:05d}_"
        f"{evento['acao']}"
    )
    pasta_evento = pasta_sessao / nome
    pasta_evento.mkdir(
        parents=True,
        exist_ok=True,
    )

    antes = evento["antes"]
    depois = evento["depois"]

    for i, frame in enumerate(antes):
        cv2.imwrite(
            str(
                pasta_evento
                / f"antes_{i:03d}.png"
            ),
            frame,
        )

    cv2.imwrite(
        str(pasta_evento / "acao.png"),
        evento["frame_acao"],
    )

    for i, frame in enumerate(depois):
        cv2.imwrite(
            str(
                pasta_evento
                / f"depois_{i:03d}.png"
            ),
            frame,
        )

    return {
        "indice": indice,
        "acao": evento["acao"],
        "codigo_tecla": evento["codigo_tecla"],
        "timestamp": evento["timestamp"],
        "pasta": str(pasta_evento),
        "frames_antes": len(antes),
        "frames_depois": len(depois),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Modo professor: observa o usuario jogando "
            "e registra contexto visual antes/depois "
            "das acoes."
        )
    )
    parser.add_argument(
        "--config",
        default="config.local.json",
    )
    parser.add_argument(
        "--saida",
        default="demonstracoes",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=8.0,
        help=(
            "Frequencia de observacao. Padrao: 8 FPS."
        ),
    )
    parser.add_argument(
        "--antes",
        type=float,
        default=0.75,
        help=(
            "Segundos de contexto antes da acao. "
            "Padrao: 0.75."
        ),
    )
    parser.add_argument(
        "--depois",
        type=float,
        default=1.0,
        help=(
            "Segundos de contexto depois da acao. "
            "Padrao: 1.0."
        ),
    )
    args = parser.parse_args()

    if args.fps <= 0:
        raise ValueError("--fps deve ser maior que 0.")

    if args.antes < 0 or args.depois < 0:
        raise ValueError(
            "--antes e --depois nao podem ser negativos."
        )

    config = carregar_configuracao_controles(
        args.config
    )

    teclas = {
        acao: config.tecla_para(acao)
        for acao in ACOES_OBSERVADAS
        if config.tecla_para(acao) is not None
    }

    if not teclas:
        print(
            "Nenhuma tecla configurada para observar."
        )
        return

    pasta_raiz = Path(args.saida)
    pasta_sessao = (
        pasta_raiz / nome_sessao()
    )
    pasta_sessao.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_eventos = (
        pasta_sessao / "eventos.jsonl"
    )

    try:
        captura = IdleSlayerCapture(
            titulo=config.titulo_janela
        )
    except IdleSlayerNaoEncontrado as erro:
        print(erro)
        return

    intervalo = 1.0 / args.fps
    quantidade_antes = max(
        1,
        int(round(args.antes * args.fps)),
    )
    historico = deque(
        maxlen=quantidade_antes
    )

    estados_teclas = {
        acao: False
        for acao in teclas
    }

    pendentes: list[dict] = []
    registrados = 0

    print("SlayerAI - Modo professor")
    print("=" * 40)
    print(f"Sessao: {pasta_sessao}")
    print(
        "Jogue normalmente. O programa observa "
        "as acoes configuradas."
    )
    print(
        "F8 encerra a sessao. Nenhuma tecla "
        "sera enviada ao jogo."
    )
    print(
        "Observando: "
        + ", ".join(
            f"{acao.value}={codigo}"
            for acao, codigo in teclas.items()
        )
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

            agora = time.time()
            novas_acoes = []

            for acao, codigo in teclas.items():
                pressionada = tecla_pressionada(
                    codigo
                )
                anterior = estados_teclas[acao]

                if pressionada and not anterior:
                    novas_acoes.append(
                        (acao, codigo)
                    )

                estados_teclas[acao] = pressionada

            for evento in pendentes:
                if (
                    agora
                    <= evento["fim_depois"]
                ):
                    evento["depois"].append(
                        frame.copy()
                    )

            concluidos = [
                evento
                for evento in pendentes
                if agora > evento["fim_depois"]
            ]

            for evento in concluidos:
                resumo = salvar_evento(
                    pasta_sessao,
                    registrados,
                    evento,
                )

                with caminho_eventos.open(
                    "a",
                    encoding="utf-8",
                ) as arquivo:
                    arquivo.write(
                        json.dumps(
                            resumo,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                registrados += 1
                print(
                    f"[{registrados}] "
                    f"{evento['acao']} registrado"
                )

            pendentes = [
                evento
                for evento in pendentes
                if evento not in concluidos
            ]

            for acao, codigo in novas_acoes:
                pendentes.append(
                    {
                        "acao": acao.value,
                        "codigo_tecla": codigo,
                        "timestamp": agora,
                        "antes": [
                            item.copy()
                            for item in historico
                        ],
                        "frame_acao": frame.copy(),
                        "depois": [],
                        "fim_depois": (
                            agora + args.depois
                        ),
                    }
                )

            historico.append(
                frame.copy()
            )

            preview = frame.copy()
            cv2.rectangle(
                preview,
                (0, 0),
                (preview.shape[1], 58),
                (0, 0, 0),
                -1,
            )
            cv2.putText(
                preview,
                "MODO PROFESSOR - jogue normalmente",
                (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                preview,
                (
                    f"eventos: {registrados} | "
                    "F8 encerra"
                ),
                (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            cv2.imshow(
                "SlayerAI - Modo professor",
                preview,
            )
            cv2.waitKey(1)

            if tecla_pressionada(
                win32con.VK_F8
            ):
                break

            gasto = (
                time.perf_counter() - inicio
            )
            restante = intervalo - gasto

            if restante > 0:
                time.sleep(restante)

    finally:
        for evento in pendentes:
            resumo = salvar_evento(
                pasta_sessao,
                registrados,
                evento,
            )

            with caminho_eventos.open(
                "a",
                encoding="utf-8",
            ) as arquivo:
                arquivo.write(
                    json.dumps(
                        resumo,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            registrados += 1

        captura.close()
        cv2.destroyAllWindows()

    print("")
    print("Sessao encerrada.")
    print(
        f"Eventos registrados: {registrados}"
    )
    print(f"Dados: {pasta_sessao}")


if __name__ == "__main__":
    main()
