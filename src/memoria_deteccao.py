from dataclasses import dataclass

from tipos_visao import Deteccao


@dataclass
class MemoriaDeteccao:
    max_falhas: int = 2
    max_deslocamento_x: float = 0.18
    confianca_reaquisicao: float = 0.55
    ultima: Deteccao | None = None
    falhas_consecutivas: int = 0
    ultima_rejeitada: bool = False

    def __post_init__(self) -> None:
        if self.max_falhas < 0:
            raise ValueError("max_falhas nao pode ser negativo.")

        if not 0 <= self.max_deslocamento_x <= 1:
            raise ValueError(
                "max_deslocamento_x deve estar entre 0 e 1."
            )

        if not 0 <= self.confianca_reaquisicao <= 1:
            raise ValueError(
                "confianca_reaquisicao deve estar entre 0 e 1."
            )

    @staticmethod
    def _centro_x(deteccao: Deteccao) -> float:
        x1, _, x2, _ = deteccao.caixa
        return (x1 + x2) / 2

    def _transicao_plausivel(
        self,
        deteccao: Deteccao,
        largura_frame: int | None,
    ) -> bool:
        if self.ultima is None or largura_frame is None:
            return True

        if largura_frame <= 0:
            return True

        deslocamento = abs(
            self._centro_x(deteccao)
            - self._centro_x(self.ultima)
        )
        deslocamento_normalizado = (
            deslocamento / largura_frame
        )

        if (
            deslocamento_normalizado
            <= self.max_deslocamento_x
        ):
            return True

        return (
            deteccao.confianca
            >= self.confianca_reaquisicao
        )

    def atualizar(
        self,
        deteccao: Deteccao | None,
        largura_frame: int | None = None,
    ) -> Deteccao | None:
        self.ultima_rejeitada = False

        if deteccao is not None:
            if self._transicao_plausivel(
                deteccao,
                largura_frame,
            ):
                self.ultima = deteccao
                self.falhas_consecutivas = 0
                return deteccao

            self.ultima_rejeitada = True
            deteccao = None

        if self.ultima is None:
            return None

        self.falhas_consecutivas += 1

        if self.falhas_consecutivas <= self.max_falhas:
            return self.ultima

        self.ultima = None
        return None
