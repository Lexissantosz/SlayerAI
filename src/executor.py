from dataclasses import dataclass, field
from typing import Protocol

from decisor import Acao, Decisao


class EmissorEntrada(Protocol):
    def pressionar(self, codigo_tecla: int) -> None:
        ...


class ExecutorAcoes:
    def executar(self, decisao: Decisao) -> None:
        raise NotImplementedError


@dataclass
class ExecutorSimulado(ExecutorAcoes):
    historico: list[Decisao] = field(default_factory=list)

    def executar(self, decisao: Decisao) -> None:
        self.historico.append(decisao)

        print(
            f"[SIMULADO] {decisao.acao.value}: "
            f"{decisao.motivo}"
        )

    @property
    def ultima_acao(self) -> Acao | None:
        if not self.historico:
            return None

        return self.historico[-1].acao


@dataclass
class ExecutorTeclas(ExecutorAcoes):
    emissor: EmissorEntrada
    mapeamento: dict[Acao, int]

    def executar(self, decisao: Decisao) -> None:
        if decisao.acao == Acao.NENHUMA:
            return

        codigo = self.mapeamento.get(decisao.acao)

        if codigo is None:
            raise KeyError(
                f"Acao sem tecla configurada: "
                f"{decisao.acao.value}"
            )

        self.emissor.pressionar(codigo)
