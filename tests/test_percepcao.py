from detector import Deteccao
from estado_jogo import TipoObjeto
from percepcao import (
    DeteccaoObjeto,
    estado_a_partir_deteccao_player,
    estado_a_partir_deteccoes,
)


def test_estado_sem_deteccao_nao_tem_player():
    estado = estado_a_partir_deteccao_player(
        1000,
        600,
        None,
    )

    assert estado.player is None


def test_estado_converte_deteccao_em_player():
    deteccao = Deteccao(
        caixa=(100, 200, 180, 360),
        confianca=0.87,
        inferencia_ms=20.0,
    )

    estado = estado_a_partir_deteccao_player(
        1000,
        600,
        deteccao,
    )

    assert estado.player is not None
    assert estado.player.tipo == TipoObjeto.PLAYER
    assert estado.player.caixa.x1 == 100
    assert estado.player.confianca == 0.87


def test_estado_aceita_varios_tipos_de_objeto():
    estado = estado_a_partir_deteccoes(
        1000,
        600,
        [
            DeteccaoObjeto(
                TipoObjeto.PLAYER,
                (100, 200, 180, 360),
                0.90,
            ),
            DeteccaoObjeto(
                TipoObjeto.INIMIGO,
                (300, 220, 360, 360),
                0.80,
            ),
            DeteccaoObjeto(
                TipoObjeto.CAIXA,
                (500, 250, 540, 310),
                0.75,
            ),
        ],
    )

    assert estado.player is not None
    assert len(
        estado.objetos_do_tipo(TipoObjeto.INIMIGO)
    ) == 1
    assert len(
        estado.objetos_do_tipo(TipoObjeto.CAIXA)
    ) == 1
