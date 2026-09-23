import pytest

from memoria_deteccao import MemoriaDeteccao
from tipos_visao import Deteccao


def det() -> Deteccao:
    return Deteccao(
        caixa=(10, 20, 30, 40),
        confianca=0.8,
        inferencia_ms=12.0,
    )


def test_mantem_deteccao_por_duas_falhas():
    memoria = MemoriaDeteccao(max_falhas=2)
    original = det()

    assert memoria.atualizar(original) == original
    assert memoria.atualizar(None) == original
    assert memoria.atualizar(None) == original
    assert memoria.atualizar(None) is None


def test_nova_deteccao_reseta_contador():
    memoria = MemoriaDeteccao(max_falhas=1)
    original = det()

    memoria.atualizar(original)
    memoria.atualizar(None)

    nova = Deteccao(
        caixa=(20, 30, 40, 50),
        confianca=0.9,
        inferencia_ms=10.0,
    )

    assert memoria.atualizar(nova) == nova
    assert memoria.falhas_consecutivas == 0


def test_rejeita_limite_negativo():
    with pytest.raises(ValueError):
        MemoriaDeteccao(max_falhas=-1)
