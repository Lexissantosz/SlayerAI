from dataclasses import dataclass


@dataclass(frozen=True)
class Deteccao:
    caixa: tuple[int, int, int, int]
    confianca: float
    inferencia_ms: float
