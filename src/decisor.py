from dataclasses import dataclass
from enum import Enum

from estado_jogo import EstadoJogo, TipoObjeto


class Acao(str, Enum):
    NENHUMA = "nenhuma"
    PULAR = "pular"
    ATACAR = "atacar"
    ATIRAR = "atirar"


@dataclass(frozen=True)
class Decisao:
    acao: Acao
    motivo: str


@dataclass(frozen=True)
class ConfiguracaoDecisor:
    distancia_pulo: float = 0.16
    distancia_ataque: float = 0.20
    distancia_tiro: float = 0.42


class DecisorBasico:
    """
    Motor de regras simples.

    Nesta fase ele nao envia teclas nem cliques. Apenas transforma
    um EstadoJogo em uma decisao explicavel.
    """

    def __init__(
        self,
        config: ConfiguracaoDecisor | None = None,
    ):
        self.config = config or ConfiguracaoDecisor()

    def decidir(self, estado: EstadoJogo) -> Decisao:
        player = estado.player

        if player is None:
            return Decisao(
                Acao.NENHUMA,
                "player nao localizado",
            )

        obstaculos = estado.objetos_a_frente(
            {TipoObjeto.OBSTACULO}
        )

        if obstaculos:
            distancia = estado.distancia_horizontal_normalizada(
                obstaculos[0]
            )

            if (
                distancia is not None
                and 0 <= distancia <= self.config.distancia_pulo
            ):
                return Decisao(
                    Acao.PULAR,
                    (
                        "obstaculo proximo "
                        f"({distancia:.3f} da largura da tela)"
                    ),
                )

        inimigos = estado.objetos_a_frente(
            {TipoObjeto.INIMIGO}
        )

        if inimigos:
            distancia = estado.distancia_horizontal_normalizada(
                inimigos[0]
            )

            if distancia is not None:
                if 0 <= distancia <= self.config.distancia_ataque:
                    return Decisao(
                        Acao.ATACAR,
                        (
                            "inimigo em alcance curto "
                            f"({distancia:.3f})"
                        ),
                    )

                if 0 <= distancia <= self.config.distancia_tiro:
                    return Decisao(
                        Acao.ATIRAR,
                        (
                            "inimigo em alcance de tiro "
                            f"({distancia:.3f})"
                        ),
                    )

        return Decisao(
            Acao.NENHUMA,
            "nenhuma ameaca prioritaria",
        )
