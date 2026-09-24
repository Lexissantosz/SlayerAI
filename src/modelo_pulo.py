from pathlib import Path

import cv2
import numpy as np


LARGURA = 96
ALTURA = 64
K_PADRAO = 5


def extrair_caracteristicas(frame: np.ndarray) -> np.ndarray:
    altura, largura = frame.shape[:2]

    topo = int(altura * 0.18)
    gameplay = frame[topo:altura, 0:largura]

    cinza = cv2.cvtColor(
        gameplay,
        cv2.COLOR_BGR2GRAY,
    )
    reduzida = cv2.resize(
        cinza,
        (LARGURA, ALTURA),
        interpolation=cv2.INTER_AREA,
    ).astype(np.float32)

    # Evita depender de cv2.HOGDescriptor, que nao
    # esta disponivel em algumas builds recentes do
    # OpenCV/Python 3.14. Usamos intensidade +
    # gradientes simples calculados com NumPy.
    intensidade = reduzida / 255.0

    grad_x = np.zeros_like(intensidade)
    grad_y = np.zeros_like(intensidade)

    grad_x[:, 1:] = (
        intensidade[:, 1:]
        - intensidade[:, :-1]
    )
    grad_y[1:, :] = (
        intensidade[1:, :]
        - intensidade[:-1, :]
    )

    vetor = np.concatenate(
        (
            intensidade.reshape(-1),
            grad_x.reshape(-1),
            grad_y.reshape(-1),
        )
    )

    return vetor.reshape(1, -1).astype(
        np.float32
    )


def criar_knn(
    amostras: np.ndarray,
    rotulos: np.ndarray,
) -> cv2.ml_KNearest:
    knn = cv2.ml.KNearest_create()
    knn.setDefaultK(K_PADRAO)
    knn.setIsClassifier(True)
    knn.train(
        amostras,
        cv2.ml.ROW_SAMPLE,
        rotulos,
    )
    return knn


def prever(
    knn: cv2.ml_KNearest,
    caracteristicas: np.ndarray,
    k: int = K_PADRAO,
) -> tuple[int, float]:
    _, resultado, vizinhos, _ = (
        knn.findNearest(
            caracteristicas,
            k,
        )
    )

    classe = int(resultado[0, 0])
    prob_pulo = float(
        np.mean(vizinhos[0] == 1)
    )

    return classe, prob_pulo


def salvar_dataset_modelo(
    caminho: str | Path,
    amostras: np.ndarray,
    rotulos: np.ndarray,
) -> None:
    caminho = Path(caminho)
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.savez_compressed(
        caminho,
        amostras=amostras,
        rotulos=rotulos,
    )


def carregar_dataset_modelo(
    caminho: str | Path,
) -> tuple[np.ndarray, np.ndarray]:
    dados = np.load(str(caminho))

    return (
        dados["amostras"].astype(np.float32),
        dados["rotulos"].astype(np.float32),
    )
