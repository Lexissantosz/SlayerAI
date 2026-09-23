import argparse
from pathlib import Path

from decisor import DecisorBasico
from estado_jogo import TipoObjeto
from executor import ExecutorSimulado
from percepcao import DeteccaoObjeto
from pipeline import CicloSlayerAI
from registro_sessao import GravadorSessao


def deteccao(
    tipo: TipoObjeto,
    caixa: tuple[int, int, int, int],
    confianca: float = 0.9,
) -> DeteccaoObjeto:
    return DeteccaoObjeto(
        tipo=tipo,
        caixa=caixa,
        confianca=confianca,
    )


def cenarios_demo() -> list[list[DeteccaoObjeto]]:
    player = deteccao(
        TipoObjeto.PLAYER,
        (100, 350, 180, 500),
        0.95,
    )

    return [
        [player],
        [
            player,
            deteccao(
                TipoObjeto.INIMIGO,
                (480, 380, 540, 500),
            ),
        ],
        [
            player,
            deteccao(
                TipoObjeto.INIMIGO,
                (250, 380, 310, 500),
            ),
        ],
        [
            player,
            deteccao(
                TipoObjeto.OBSTACULO,
                (220, 400, 280, 500),
            ),
        ],
        [],
    ]


def executar_dry_run(
    caminho_log: str | Path,
) -> list[str]:
    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )
    gravador = GravadorSessao(caminho_log)

    acoes = []

    for indice, deteccoes in enumerate(
        cenarios_demo(),
        start=1,
    ):
        resultado = ciclo.processar_deteccoes(
            largura=1000,
            altura=600,
            deteccoes=deteccoes,
        )

        gravador.registrar(
            frame=indice,
            estado=resultado.estado,
            decisao=resultado.decisao,
        )

        acoes.append(
            resultado.decisao.acao.value
        )

    return acoes


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Executa o pipeline completo sem enviar "
            "qualquer comando ao jogo."
        )
    )
    parser.add_argument(
        "--saida",
        default="sessoes/dry_run.jsonl",
        help=(
            "Arquivo JSONL para registrar a sessao. "
            "Padrao: sessoes/dry_run.jsonl"
        ),
    )
    args = parser.parse_args()

    print("SlayerAI - Dry-run")
    print("=" * 40)
    print(
        "Modo seguro: nenhuma tecla sera enviada."
    )
    print("")

    acoes = executar_dry_run(args.saida)

    print("")
    print(
        f"Sessao salva em: {args.saida}"
    )
    print(
        "Acoes: "
        + " -> ".join(acoes)
    )


if __name__ == "__main__":
    main()
