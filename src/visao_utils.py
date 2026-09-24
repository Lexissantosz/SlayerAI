from dataclasses import dataclass


@dataclass(frozen=True)
class ROI:
    x: float
    y: float
    largura: float
    altura: float


def parse_roi(valor: str | None) -> ROI | None:
    if valor is None or not valor.strip():
        return None

    partes = [parte.strip() for parte in valor.split(",")]

    if len(partes) != 4:
        raise ValueError(
            "ROI deve ter quatro valores: x,y,largura,altura"
        )

    x, y, largura, altura = map(float, partes)

    if (
        x < 0
        or y < 0
        or largura <= 0
        or altura <= 0
        or x > 1
        or y > 1
        or largura > 1
        or altura > 1
        or x + largura > 1
        or y + altura > 1
    ):
        raise ValueError(
            "ROI deve usar valores normalizados entre 0 e 1 "
            "e permanecer dentro da imagem."
        )

    return ROI(x, y, largura, altura)


def calcular_roi_pixels(
    largura_frame: int,
    altura_frame: int,
    roi: ROI | None,
) -> tuple[int, int, int, int]:
    if largura_frame <= 0 or altura_frame <= 0:
        raise ValueError("Dimensoes do frame devem ser positivas.")

    if roi is None:
        return 0, 0, largura_frame, altura_frame

    x1 = int(round(roi.x * largura_frame))
    y1 = int(round(roi.y * altura_frame))
    x2 = int(round((roi.x + roi.largura) * largura_frame))
    y2 = int(round((roi.y + roi.altura) * altura_frame))

    x1 = max(0, min(x1, largura_frame - 1))
    y1 = max(0, min(y1, altura_frame - 1))
    x2 = max(x1 + 1, min(x2, largura_frame))
    y2 = max(y1 + 1, min(y2, altura_frame))

    return x1, y1, x2, y2


def suavizar_caixa(
    anterior: tuple[int, int, int, int] | None,
    atual: tuple[int, int, int, int],
    alpha: float,
) -> tuple[int, int, int, int]:
    if anterior is None or alpha >= 1:
        return atual

    if alpha <= 0:
        return anterior

    return tuple(
        int(round(antigo * (1 - alpha) + novo * alpha))
        for antigo, novo in zip(anterior, atual)
    )
