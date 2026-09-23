from controle_acoes import (
    ExecutorComCooldown,
    LimitadorAcoes,
)
from decisor import Acao, Decisao
from executor import ExecutorSimulado


def test_limitador_bloqueia_repeticao_rapida():
    limitador = LimitadorAcoes(
        {Acao.PULAR: 0.5}
    )

    assert limitador.pode_executar(
        Acao.PULAR,
        agora=10.0,
    )

    limitador.registrar(
        Acao.PULAR,
        agora=10.0,
    )

    assert not limitador.pode_executar(
        Acao.PULAR,
        agora=10.2,
    )
    assert limitador.pode_executar(
        Acao.PULAR,
        agora=10.5,
    )


def test_executor_com_cooldown_evitaria_spam():
    interno = ExecutorSimulado()
    limitador = LimitadorAcoes(
        {Acao.PULAR: 999.0}
    )
    executor = ExecutorComCooldown(
        interno,
        limitador,
    )

    decisao = Decisao(
        Acao.PULAR,
        "obstaculo",
    )

    executor.executar(decisao)
    executor.executar(decisao)

    assert len(interno.historico) == 1


def test_nenhuma_acao_continua_registravel():
    interno = ExecutorSimulado()
    executor = ExecutorComCooldown(
        interno,
        LimitadorAcoes({}),
    )

    executor.executar(
        Decisao(
            Acao.NENHUMA,
            "sem ameaca",
        )
    )

    assert len(interno.historico) == 1
