from dataclasses import dataclass, field
from enum import Enum


class TipoObjeto(str, Enum):
    PLAYER = "player"
    INIMIGO = "inimigo"
    MOEDA = "moeda"
    GEMA = "gema"
    CAIXA = "caixa"
    CHAVE = "chave"
    OBSTACULO = "obstaculo"
    PLATAFORMA = "plataforma"
    DESCONHECIDO = "desconhecido"


@dataclass(frozen=True)
class Caixa:
    x1: int
    y1: int
    x2: int
    y2: int

    def __post_init__(self) -> None:
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError("Caixa invalida.")

    @property
    def largura(self) -> int:
        return self.x2 - self.x1

    @property
    def altura(self) -> int:
        return self.y2 - self.y1

    @property
    def centro_x(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def centro_y(self) -> float:
        return (self.y1 + self.y2) / 2


@dataclass(frozen=True)
class ObjetoVisivel:
    tipo: TipoObjeto
    caixa: Caixa
    confianca: float = 1.0

    def __post_init__(self) -> None:
        if not 0 <= self.confianca <= 1:
            raise ValueError("Confianca deve estar entre 0 e 1.")


@dataclass
class EstadoJogo:
    largura: int
    altura: int
    objetos: list[ObjetoVisivel] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.largura <= 0 or self.altura <= 0:
            raise ValueError("Dimensoes do frame devem ser positivas.")

    @property
    def player(self) -> ObjetoVisivel | None:
        candidatos = [
            objeto
            for objeto in self.objetos
            if objeto.tipo == TipoObjeto.PLAYER
        ]

        if not candidatos:
            return None

        return max(
            candidatos,
            key=lambda objeto: objeto.confianca,
        )

    def objetos_do_tipo(
        self,
        tipo: TipoObjeto,
    ) -> list[ObjetoVisivel]:
        return [
            objeto
            for objeto in self.objetos
            if objeto.tipo == tipo
        ]

    def objetos_a_frente(
        self,
        tipos: set[TipoObjeto] | None = None,
    ) -> list[ObjetoVisivel]:
        player = self.player

        if player is None:
            return []

        candidatos = [
            objeto
            for objeto in self.objetos
            if objeto.tipo != TipoObjeto.PLAYER
            and objeto.caixa.centro_x >= player.caixa.centro_x
            and (tipos is None or objeto.tipo in tipos)
        ]

        return sorted(
            candidatos,
            key=lambda objeto: objeto.caixa.centro_x,
        )

    def distancia_horizontal_normalizada(
        self,
        objeto: ObjetoVisivel,
    ) -> float | None:
        player = self.player

        if player is None:
            return None

        distancia = (
            objeto.caixa.centro_x
            - player.caixa.centro_x
        )

        return distancia / self.largura
