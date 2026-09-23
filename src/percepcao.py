from detector import Deteccao
from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)


def estado_a_partir_deteccao_player(
    largura: int,
    altura: int,
    deteccao: Deteccao | None,
) -> EstadoJogo:
    objetos: list[ObjetoVisivel] = []

    if deteccao is not None:
        x1, y1, x2, y2 = deteccao.caixa

        objetos.append(
            ObjetoVisivel(
                tipo=TipoObjeto.PLAYER,
                caixa=Caixa(x1, y1, x2, y2),
                confianca=deteccao.confianca,
            )
        )

    return EstadoJogo(
        largura=largura,
        altura=altura,
        objetos=objetos,
    )
