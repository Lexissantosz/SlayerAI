from decisor import Acao, DecisorBasico
from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)


def estado_com(
    extras: list[ObjetoVisivel],
) -> EstadoJogo:
    player = ObjetoVisivel(
        TipoObjeto.PLAYER,
        Caixa(100, 350, 180, 500),
    )

    return EstadoJogo(
        1000,
        600,
        [player, *extras],
    )


def test_sem_player_nao_age():
    decisao = DecisorBasico().decidir(
        EstadoJogo(1000, 600, [])
    )

    assert decisao.acao == Acao.NENHUMA


def test_obstaculo_proximo_prioriza_pulo():
    obstaculo = ObjetoVisivel(
        TipoObjeto.OBSTACULO,
        Caixa(220, 400, 280, 500),
    )
    inimigo = ObjetoVisivel(
        TipoObjeto.INIMIGO,
        Caixa(240, 380, 300, 500),
    )

    decisao = DecisorBasico().decidir(
        estado_com([inimigo, obstaculo])
    )

    assert decisao.acao == Acao.PULAR


def test_inimigo_curto_alcance_ataca():
    inimigo = ObjetoVisivel(
        TipoObjeto.INIMIGO,
        Caixa(250, 380, 310, 500),
    )

    decisao = DecisorBasico().decidir(
        estado_com([inimigo])
    )

    assert decisao.acao == Acao.ATACAR


def test_inimigo_medio_alcance_atira():
    inimigo = ObjetoVisivel(
        TipoObjeto.INIMIGO,
        Caixa(400, 380, 460, 500),
    )

    decisao = DecisorBasico().decidir(
        estado_com([inimigo])
    )

    assert decisao.acao == Acao.ATIRAR


def test_sem_ameaca_fica_parado():
    decisao = DecisorBasico().decidir(
        estado_com([])
    )

    assert decisao.acao == Acao.NENHUMA
