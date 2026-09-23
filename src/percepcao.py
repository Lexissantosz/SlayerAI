from dataclasses import dataclass

from detector import Deteccao
from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)


@dataclass(frozen=True)
class DeteccaoObjeto:
    tipo: TipoObjeto
    caixa: tuple[int, int, int, int]
    confianca: float


def objeto_visivel_de_deteccao(
    deteccao: DeteccaoObjeto,
) -> ObjetoVisivel:
    x1, y1, x2, y2 = deteccao.caixa

    return ObjetoVisivel(
        tipo=deteccao.tipo,
        caixa=Caixa(x1, y1, x2, y2),
        confianca=deteccao.confianca,
    )


def estado_a_partir_deteccoes(
    largura: int,
    altura: int,
    deteccoes: list[DeteccaoObjeto],
) -> EstadoJogo:
    objetos = [
        objeto_visivel_de_deteccao(deteccao)
        for deteccao in deteccoes
    ]

    return EstadoJogo(
        largura=largura,
        altura=altura,
        objetos=objetos,
    )


def estado_a_partir_deteccao_player(
    largura: int,
    altura: int,
    deteccao: Deteccao | None,
) -> EstadoJogo:
    deteccoes: list[DeteccaoObjeto] = []

    if deteccao is not None:
        deteccoes.append(
            DeteccaoObjeto(
                tipo=TipoObjeto.PLAYER,
                caixa=deteccao.caixa,
                confianca=deteccao.confianca,
            )
        )

    return estado_a_partir_deteccoes(
        largura=largura,
        altura=altura,
        deteccoes=deteccoes,
    )
