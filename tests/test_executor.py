from decisor import Acao, Decisao
from executor import ExecutorSimulado


def test_executor_simulado_registra_historico():
    executor = ExecutorSimulado()

    executor.executar(
        Decisao(
            Acao.PULAR,
            "teste",
        )
    )

    assert len(executor.historico) == 1
    assert executor.ultima_acao == Acao.PULAR
