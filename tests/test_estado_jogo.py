from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)


def test_player_escolhe_maior_confianca():
    estado = EstadoJogo(
        1000,
        600,
        [
            ObjetoVisivel(
                TipoObjeto.PLAYER,
                Caixa(100, 100, 150, 200),
                0.60,
            ),
            ObjetoVisivel(
                TipoObjeto.PLAYER,
                Caixa(110, 100, 160, 200),
                0.90,
            ),
        ],
    )

    assert estado.player is not None
    assert estado.player.confianca == 0.90


def test_objetos_a_frente_ignora_objetos_atras():
    estado = EstadoJogo(
        1000,
        600,
        [
            ObjetoVisivel(
                TipoObjeto.PLAYER,
                Caixa(100, 100, 200, 200),
            ),
            ObjetoVisivel(
                TipoObjeto.INIMIGO,
                Caixa(20, 100, 80, 200),
            ),
            ObjetoVisivel(
                TipoObjeto.INIMIGO,
                Caixa(300, 100, 360, 200),
            ),
        ],
    )

    objetos = estado.objetos_a_frente(
        {TipoObjeto.INIMIGO}
    )

    assert len(objetos) == 1
    assert objetos[0].caixa.x1 == 300


def test_distancia_horizontal_normalizada():
    player = ObjetoVisivel(
        TipoObjeto.PLAYER,
        Caixa(100, 100, 200, 200),
    )
    inimigo = ObjetoVisivel(
        TipoObjeto.INIMIGO,
        Caixa(300, 100, 400, 200),
    )
    estado = EstadoJogo(
        1000,
        600,
        [player, inimigo],
    )

    assert (
        estado.distancia_horizontal_normalizada(inimigo)
        == 0.2
    )
