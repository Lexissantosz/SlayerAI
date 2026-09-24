import json
from dataclasses import dataclass
from pathlib import Path

from decisor import Acao


@dataclass(frozen=True)
class ConfiguracaoControles:
    titulo_janela: str
    duracao_pressao: float
    teclas: dict[Acao, int | None]

    def tecla_para(self, acao: Acao) -> int | None:
        return self.teclas.get(acao)


def carregar_configuracao_controles(
    caminho: str | Path,
) -> ConfiguracaoControles:
    caminho = Path(caminho)

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        dados = json.load(arquivo)

    titulo = dados.get(
        "titulo_janela",
        "Idle Slayer",
    )
    duracao = float(
        dados.get(
            "duracao_pressao",
            0.03,
        )
    )

    if not titulo.strip():
        raise ValueError(
            "titulo_janela nao pode ser vazio."
        )

    if duracao < 0:
        raise ValueError(
            "duracao_pressao nao pode ser negativa."
        )

    teclas_json = dados.get("teclas", {})

    teclas: dict[Acao, int | None] = {}

    for acao in (
        Acao.PULAR,
        Acao.ATACAR,
        Acao.ATIRAR,
    ):
        valor = teclas_json.get(
            acao.value
        )

        if valor is not None:
            valor = int(valor)

            if valor < 0 or valor > 255:
                raise ValueError(
                    f"Codigo de tecla invalido "
                    f"para {acao.value}: {valor}"
                )

        teclas[acao] = valor

    return ConfiguracaoControles(
        titulo_janela=titulo,
        duracao_pressao=duracao,
        teclas=teclas,
    )


def mapeamento_configurado(
    config: ConfiguracaoControles,
) -> dict[Acao, int]:
    return {
        acao: codigo
        for acao, codigo in config.teclas.items()
        if codigo is not None
    }
