import pytest

from decisor import Acao, Decisao
from executor import ExecutorTeclas


class EmissorFake:
    def __init__(self):
        self.teclas = []

    def pressionar(self, codigo_tecla: int) -> None:
        self.teclas.append(codigo_tecla)


def test_executor_teclas_envia_tecla_configurada():
    emissor = EmissorFake()
    executor = ExecutorTeclas(
        emissor=emissor,
        mapeamento={
            Acao.PULAR: 32,
        },
    )

    executor.executar(
        Decisao(
            Acao.PULAR,
            "teste",
        )
    )

    assert emissor.teclas == [32]


def test_executor_teclas_ignora_nenhuma():
    emissor = EmissorFake()
    executor = ExecutorTeclas(
        emissor=emissor,
        mapeamento={},
    )

    executor.executar(
        Decisao(
            Acao.NENHUMA,
            "sem acao",
        )
    )

    assert emissor.teclas == []


def test_executor_teclas_rejeita_acao_sem_mapeamento():
    emissor = EmissorFake()
    executor = ExecutorTeclas(
        emissor=emissor,
        mapeamento={},
    )

    with pytest.raises(KeyError):
        executor.executar(
            Decisao(
                Acao.ATACAR,
                "teste",
            )
        )
