import argparse
import time

from configuracao import carregar_configuracao_controles
from decisor import Acao, Decisao
from entrada_win32 import EntradaWin32
from executor import ExecutorTeclas


ACOES_PERMITIDAS = {
    "pular": Acao.PULAR,
    "atacar": Acao.ATACAR,
    "atirar": Acao.ATIRAR,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Envia uma unica acao configurada para a janela "
            "do Idle Slayer, sem roubar o foco."
        )
    )
    parser.add_argument(
        "--acao",
        choices=sorted(ACOES_PERMITIDAS),
        required=True,
    )
    parser.add_argument(
        "--config",
        default="config.local.json",
    )
    parser.add_argument(
        "--atraso",
        type=float,
        default=3.0,
        help="Segundos antes do envio. Padrao: 3.",
    )
    args = parser.parse_args()

    config = carregar_configuracao_controles(
        args.config
    )
    acao = ACOES_PERMITIDAS[args.acao]
    codigo = config.tecla_para(acao)

    if codigo is None:
        print(
            f"Acao sem tecla configurada: "
            f"{acao.value}"
        )
        return

    emissor = EntradaWin32(
        titulo=config.titulo_janela,
        duracao_pressao=config.duracao_pressao,
    )
    executor = ExecutorTeclas(
        emissor=emissor,
        mapeamento={acao: codigo},
    )

    atraso = max(0.0, args.atraso)

    print("SlayerAI - teste de entrada real")
    print("=" * 40)
    print(f"Janela: {config.titulo_janela}")
    print(f"Acao: {acao.value}")
    print(f"Codigo: {codigo}")
    print(
        "Sera enviado UM unico comando "
        f"em {atraso:.1f}s."
    )

    if atraso > 0:
        time.sleep(atraso)

    executor.executar(
        Decisao(
            acao=acao,
            motivo="teste manual de entrada real",
        )
    )

    print("Comando enviado uma unica vez.")


if __name__ == "__main__":
    main()
