from dataclasses import dataclass, field

from decisor import Acao, Decisao


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
