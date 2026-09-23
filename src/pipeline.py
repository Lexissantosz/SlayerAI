from dataclasses import dataclass

from decisor import Decisao, DecisorBasico
from detector import Deteccao
from estado_jogo import EstadoJogo
from executor import ExecutorAcoes
from percepcao import estado_a_partir_deteccao_player


@dataclass(frozen=True)
class ResultadoCiclo:
    estado: EstadoJogo
    decisao: Decisao


class CicloSlayerAI:
    def __init__(
        self,
        decisor: DecisorBasico,
        executor: ExecutorAcoes,
    ):
        self.decisor = decisor
        self.executor = executor

    def processar(
        self,
        largura: int,
        altura: int,
        deteccao_player: Deteccao | None,
    ) -> ResultadoCiclo:
        estado = estado_a_partir_deteccao_player(
            largura=largura,
            altura=altura,
            deteccao=deteccao_player,
        )

        decisao = self.decisor.decidir(estado)
        self.executor.executar(decisao)

        return ResultadoCiclo(
            estado=estado,
            decisao=decisao,
        )
