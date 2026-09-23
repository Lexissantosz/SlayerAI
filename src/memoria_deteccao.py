from dataclasses import dataclass

from tipos_visao import Deteccao


@dataclass
class MemoriaDeteccao:
    max_falhas: int = 2
    ultima: Deteccao | None = None
    falhas_consecutivas: int = 0

    def __post_init__(self) -> None:
        if self.max_falhas < 0:
            raise ValueError("max_falhas nao pode ser negativo.")

    def atualizar(
        self,
        deteccao: Deteccao | None,
    ) -> Deteccao | None:
        if deteccao is not None:
            self.ultima = deteccao
            self.falhas_consecutivas = 0
            return deteccao

        if self.ultima is None:
            return None

        self.falhas_consecutivas += 1

        if self.falhas_consecutivas <= self.max_falhas:
            return self.ultima

        self.ultima = None
        return None
