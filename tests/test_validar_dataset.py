from validar_dataset import validar_linha_yolo


def test_rotulo_yolo_valido():
    valido, motivo = validar_linha_yolo(
        "0 0.500000 0.500000 0.200000 0.300000"
    )

    assert valido is True
    assert motivo is None


def test_rotulo_rejeita_classe_desconhecida():
    valido, _ = validar_linha_yolo(
        "1 0.500000 0.500000 0.200000 0.300000"
    )

    assert valido is False


def test_rotulo_rejeita_caixa_fora_da_imagem():
    valido, _ = validar_linha_yolo(
        "0 0.050000 0.500000 0.200000 0.300000"
    )

    assert valido is False
