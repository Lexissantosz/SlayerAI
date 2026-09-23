import pytest

from memoria_deteccao import MemoriaDeteccao
from tipos_visao import Deteccao


def det(
    caixa=(10, 20, 30, 40),
    confianca=0.8,
) -> Deteccao:
    return Deteccao(
        caixa=caixa,
        confianca=confianca,
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

    nova = det(
        caixa=(20, 30, 40, 50),
        confianca=0.9,
    )

    assert memoria.atualizar(nova) == nova
    assert memoria.falhas_consecutivas == 0


def test_rejeita_salto_horizontal_fraco():
    memoria = MemoriaDeteccao(
        max_falhas=2,
        max_deslocamento_x=0.18,
        confianca_reaquisicao=0.55,
    )
    original = det(
        caixa=(80, 200, 140, 320),
        confianca=0.8,
    )
    falso = det(
        caixa=(600, 200, 700, 330),
        confianca=0.30,
    )

    memoria.atualizar(
        original,
        largura_frame=1000,
    )
    mantida = memoria.atualizar(
        falso,
        largura_frame=1000,
    )

    assert mantida == original
    assert memoria.ultima_rejeitada is True


def test_aceita_reaquisicao_distante_com_confianca_forte():
    memoria = MemoriaDeteccao(
        max_deslocamento_x=0.18,
        confianca_reaquisicao=0.55,
    )
    memoria.atualizar(
        det(
            caixa=(80, 200, 140, 320),
            confianca=0.8,
        ),
        largura_frame=1000,
    )

    nova = det(
        caixa=(600, 200, 700, 330),
        confianca=0.75,
    )

    assert (
        memoria.atualizar(
            nova,
            largura_frame=1000,
        )
        == nova
    )
    assert memoria.ultima_rejeitada is False


def test_rejeita_limite_negativo():
    with pytest.raises(ValueError):
        MemoriaDeteccao(max_falhas=-1)
