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


class KNNNumpy:
    def __init__(
        self,
        amostras: np.ndarray,
        rotulos: np.ndarray,
    ):
        if amostras.ndim != 2:
            raise ValueError(
                "amostras deve ser uma matriz 2D."
            )

        if len(amostras) != len(rotulos):
            raise ValueError(
                "amostras e rotulos devem ter "
                "o mesmo tamanho."
            )

        if len(amostras) == 0:
            raise ValueError(
                "Nao ha amostras para o KNN."
            )

        self.amostras = np.ascontiguousarray(
            amostras,
            dtype=np.float32,
        )
        self.rotulos = np.asarray(
            rotulos,
            dtype=np.int8,
        ).reshape(-1)
        self.normas = np.sum(
            self.amostras * self.amostras,
            axis=1,
        )


def criar_knn(
    amostras: np.ndarray,
    rotulos: np.ndarray,
) -> KNNNumpy:
    # Implementacao propria para nao depender de
    # cv2.ml, ausente em algumas builds do OpenCV
    # usadas com Python 3.14.
    return KNNNumpy(
        amostras=amostras,
        rotulos=rotulos,
    )


def prever(
    knn: KNNNumpy,
    caracteristicas: np.ndarray,
    k: int = K_PADRAO,
) -> tuple[int, float]:
    consulta = np.asarray(
        caracteristicas,
        dtype=np.float32,
    ).reshape(-1)

    if consulta.size != knn.amostras.shape[1]:
        raise ValueError(
            "Dimensao da amostra diferente do modelo."
        )

    k_efetivo = max(
        1,
        min(int(k), len(knn.rotulos)),
    )

    # Distancia euclidiana ao quadrado usando produto
    # escalar, evitando criar uma matriz gigante de
    # diferencas a cada frame.
    distancias = (
        knn.normas
        + float(np.dot(consulta, consulta))
        - 2.0 * np.dot(
            knn.amostras,
            consulta,
        )
    )

    indices = np.argpartition(
        distancias,
        k_efetivo - 1,
    )[:k_efetivo]

    vizinhos = knn.rotulos[indices]
    prob_pulo = float(
        np.mean(vizinhos == 1)
    )
    classe = int(
        prob_pulo >= 0.5
    )

    return classe, prob_pulo

def salvar_dataset_modelo(
    caminho: str | Path,
    amostras: np.ndarray,
    rotulos: np.ndarray,
    limiar: float = 0.60,
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
        limiar=np.asarray(
            [limiar],
            dtype=np.float32,
        ),
    )


def carregar_dataset_modelo(
    caminho: str | Path,
) -> tuple[np.ndarray, np.ndarray]:
    dados = np.load(str(caminho))

    return (
        dados["amostras"].astype(np.float32),
        dados["rotulos"].astype(np.float32),
    )


def carregar_limiar_modelo(
    caminho: str | Path,
    padrao: float = 0.60,
) -> float:
    dados = np.load(str(caminho))

    if "limiar" not in dados:
        return padrao

    return float(
        dados["limiar"].reshape(-1)[0]
    )
