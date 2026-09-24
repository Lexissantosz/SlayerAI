from decisor import DecisorBasico
from estado_jogo import (
    Caixa,
    EstadoJogo,
    ObjetoVisivel,
    TipoObjeto,
)


def objeto(
    tipo: TipoObjeto,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    confianca: float = 1.0,
) -> ObjetoVisivel:
    return ObjetoVisivel(
        tipo=tipo,
        caixa=Caixa(x1, y1, x2, y2),
        confianca=confianca,
    )


def main() -> None:
    decisor = DecisorBasico()

    cenarios = {
        "sem ameacas": EstadoJogo(
            1000,
            600,
            [
                objeto(
                    TipoObjeto.PLAYER,
                    120,
                    380,
                    180,
                    500,
                ),
            ],
        ),
        "obstaculo perto": EstadoJogo(
            1000,
            600,
            [
                objeto(
                    TipoObjeto.PLAYER,
                    120,
                    380,
                    180,
                    500,
                ),
                objeto(
                    TipoObjeto.OBSTACULO,
                    250,
                    420,
                    300,
                    500,
                ),
            ],
        ),
        "inimigo perto": EstadoJogo(
            1000,
            600,
            [
                objeto(
                    TipoObjeto.PLAYER,
                    120,
                    380,
                    180,
                    500,
                ),
                objeto(
                    TipoObjeto.INIMIGO,
                    260,
                    390,
                    320,
                    490,
                ),
            ],
        ),
        "inimigo longe": EstadoJogo(
            1000,
            600,
            [
                objeto(
                    TipoObjeto.PLAYER,
                    120,
                    380,
                    180,
                    500,
                ),
                objeto(
                    TipoObjeto.INIMIGO,
                    480,
                    390,
                    540,
                    490,
                ),
            ],
        ),
    }

    print("SlayerAI - Simulador de decisoes")
    print("=" * 40)

    for nome, estado in cenarios.items():
        decisao = decisor.decidir(estado)
        print(
            f"{nome:18} -> "
            f"{decisao.acao.value:8} | "
            f"{decisao.motivo}"
        )


if __name__ == "__main__":
    main()
