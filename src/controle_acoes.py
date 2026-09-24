import time
from dataclasses import dataclass, field

from decisor import Acao, Decisao
from executor import ExecutorAcoes


@dataclass
class LimitadorAcoes:
    cooldowns: dict[Acao, float]
    ultimas_execucoes: dict[Acao, float] = field(
        default_factory=dict
    )

    def pode_executar(
        self,
        acao: Acao,
        agora: float | None = None,
    ) -> bool:
        if acao == Acao.NENHUMA:
            return True

        momento = (
            time.monotonic()
            if agora is None
            else agora
        )

        cooldown = max(
            0.0,
            self.cooldowns.get(acao, 0.0),
        )
        ultima = self.ultimas_execucoes.get(acao)

        return (
            ultima is None
            or momento - ultima >= cooldown
        )

    def registrar(
        self,
        acao: Acao,
        agora: float | None = None,
    ) -> None:
        if acao == Acao.NENHUMA:
            return

        momento = (
            time.monotonic()
            if agora is None
            else agora
        )
        self.ultimas_execucoes[acao] = momento


class ExecutorComCooldown(ExecutorAcoes):
    def __init__(
        self,
        executor: ExecutorAcoes,
        limitador: LimitadorAcoes,
    ):
        self.executor = executor
        self.limitador = limitador

    def executar(self, decisao: Decisao) -> None:
        if decisao.acao == Acao.NENHUMA:
            self.executor.executar(decisao)
            return

        if not self.limitador.pode_executar(
            decisao.acao
        ):
            return

        self.executor.executar(decisao)
        self.limitador.registrar(decisao.acao)
