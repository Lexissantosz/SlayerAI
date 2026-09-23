import argparse
from pathlib import Path

from configuracao import (
    carregar_configuracao_controles,
    mapeamento_configurado,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Valida a configuracao local de controles "
            "sem enviar nenhuma tecla."
        )
    )
    parser.add_argument(
        "--config",
        default="config.local.json",
        help=(
            "Arquivo JSON de configuracao. "
            "Padrao: config.local.json"
        ),
    )
    args = parser.parse_args()

    caminho = Path(args.config)

    if not caminho.exists():
        print(
            f"Configuracao nao encontrada: "
            f"{caminho}"
        )
        print(
            "Copie config.example.json para "
            "config.local.json e preencha depois."
        )
        return

    config = carregar_configuracao_controles(
        caminho
    )
    mapeamento = mapeamento_configurado(config)

    print("SlayerAI - Configuracao de controles")
    print("=" * 40)
    print(f"Janela: {config.titulo_janela}")
    print(
        f"Duracao: "
        f"{config.duracao_pressao:.3f}s"
    )

    if not mapeamento:
        print("Teclas configuradas: nenhuma")
        return

    print("Teclas configuradas:")

    for acao, codigo in mapeamento.items():
        print(
            f"- {acao.value}: {codigo}"
        )


if __name__ == "__main__":
    main()
