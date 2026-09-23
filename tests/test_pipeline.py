from decisor import Acao, DecisorBasico
from detector import Deteccao
from estado_jogo import TipoObjeto
from executor import ExecutorSimulado
from percepcao import DeteccaoObjeto
from pipeline import CicloSlayerAI


def test_pipeline_sem_player_nao_age():
    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )

    resultado = ciclo.processar(
        1000,
        600,
        None,
    )

    assert resultado.estado.player is None
    assert resultado.decisao.acao == Acao.NENHUMA
    assert executor.ultima_acao == Acao.NENHUMA


def test_pipeline_com_player_cria_estado():
    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )

    deteccao = Deteccao(
        caixa=(100, 200, 180, 360),
        confianca=0.91,
        inferencia_ms=15.0,
    )

    resultado = ciclo.processar(
        1000,
        600,
        deteccao,
    )

    assert resultado.estado.player is not None
    assert resultado.estado.player.confianca == 0.91


def test_pipeline_multiclasse_pode_decidir_pulo():
    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )

    resultado = ciclo.processar_deteccoes(
        1000,
        600,
        [
            DeteccaoObjeto(
                TipoObjeto.PLAYER,
                (100, 350, 180, 500),
                0.95,
            ),
            DeteccaoObjeto(
                TipoObjeto.OBSTACULO,
                (220, 400, 280, 500),
                0.90,
            ),
        ],
    )

    assert resultado.decisao.acao == Acao.PULAR
