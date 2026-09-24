import json

import pytest

from configuracao import (
    carregar_configuracao_controles,
    mapeamento_configurado,
)
from decisor import Acao


def salvar(tmp_path, dados):
    caminho = tmp_path / "config.json"
    caminho.write_text(
        json.dumps(dados),
        encoding="utf-8",
    )
    return caminho


def test_carrega_configuracao_com_teclas_nulas(
    tmp_path,
):
    caminho = salvar(
        tmp_path,
        {
            "titulo_janela": "Idle Slayer",
            "duracao_pressao": 0.03,
            "teclas": {
                "pular": None,
                "atacar": None,
                "atirar": None,
            },
        },
    )

    config = carregar_configuracao_controles(
        caminho
    )

    assert config.tecla_para(
        Acao.PULAR
    ) is None
    assert mapeamento_configurado(config) == {}


def test_carrega_codigos_configurados(tmp_path):
    caminho = salvar(
        tmp_path,
        {
            "titulo_janela": "Idle Slayer",
            "duracao_pressao": 0.05,
            "teclas": {
                "pular": 32,
                "atacar": 65,
                "atirar": 66,
            },
        },
    )

    config = carregar_configuracao_controles(
        caminho
    )

    assert config.tecla_para(
        Acao.PULAR
    ) == 32
    assert mapeamento_configurado(config)[
        Acao.ATACAR
    ] == 65


def test_rejeita_codigo_fora_do_intervalo(
    tmp_path,
):
    caminho = salvar(
        tmp_path,
        {
            "teclas": {
                "pular": 999,
            },
        },
    )

    with pytest.raises(ValueError):
        carregar_configuracao_controles(
            caminho
        )


def test_rejeita_duracao_negativa(tmp_path):
    caminho = salvar(
        tmp_path,
        {
            "duracao_pressao": -0.1,
        },
    )

    with pytest.raises(ValueError):
        carregar_configuracao_controles(
            caminho
        )
