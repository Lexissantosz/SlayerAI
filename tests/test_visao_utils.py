import pytest

from visao_utils import (
    calcular_roi_pixels,
    parse_roi,
    suavizar_caixa,
)


def test_parse_roi_valida():
    roi = parse_roi("0,0.1,0.5,0.8")

    assert roi is not None
    assert roi.x == 0
    assert roi.y == 0.1
    assert roi.largura == 0.5
    assert roi.altura == 0.8


def test_parse_roi_rejeita_fora_da_imagem():
    with pytest.raises(ValueError):
        parse_roi("0.8,0,0.5,1")


def test_calcular_roi_pixels_frame_inteiro():
    assert calcular_roi_pixels(720, 480, None) == (
        0,
        0,
        720,
        480,
    )


def test_suavizar_caixa():
    resultado = suavizar_caixa(
        (0, 0, 100, 100),
        (10, 20, 110, 120),
        0.5,
    )

    assert resultado == (5, 10, 105, 110)
