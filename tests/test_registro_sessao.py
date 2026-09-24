import json

from decisor import Acao, Decisao
from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)
from registro_sessao import (
    GravadorSessao,
    carregar_registros,
    deteccoes_do_registro,
)


def test_grava_e_carrega_sessao(tmp_path):
    caminho = tmp_path / "sessao.jsonl"
    gravador = GravadorSessao(caminho)

    estado = EstadoJogo(
        1000,
        600,
        [
            ObjetoVisivel(
                TipoObjeto.PLAYER,
                Caixa(100, 200, 180, 360),
                0.91,
            )
        ],
    )

    gravador.registrar(
        1,
        estado,
        Decisao(
            Acao.NENHUMA,
            "teste",
        ),
    )

    registros = carregar_registros(caminho)

    assert len(registros) == 1
    assert registros[0]["frame"] == 1
    assert (
        registros[0]["deteccoes"][0]["tipo"]
        == "player"
    )


def test_reconstroi_deteccoes(tmp_path):
    caminho = tmp_path / "sessao.jsonl"
    caminho.write_text(
        json.dumps(
            {
                "frame": 1,
                "largura": 1000,
                "altura": 600,
                "deteccoes": [
                    {
                        "tipo": "inimigo",
                        "caixa": [10, 20, 30, 40],
                        "confianca": 0.8,
                    }
                ],
                "decisao": {
                    "acao": "atacar",
                    "motivo": "teste",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    registro = carregar_registros(caminho)[0]
    deteccoes = deteccoes_do_registro(
        registro
    )

    assert len(deteccoes) == 1
    assert deteccoes[0].tipo == TipoObjeto.INIMIGO
    assert deteccoes[0].caixa == (
        10,
        20,
        30,
        40,
    )
