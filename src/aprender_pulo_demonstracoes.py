import argparse
from pathlib import Path

import cv2
import numpy as np

from modelo_pulo import (
    criar_knn,
    extrair_caracteristicas,
    prever,
    salvar_dataset_modelo,
)


ROOT = Path(__file__).resolve().parent.parent
DEMONSTRACOES = ROOT / "demonstracoes"
MODELO = ROOT / "modelos/pulo_demo_v01.npz"


def encontrar_sessao(
    caminho: str | None,
) -> Path:
    if caminho:
        sessao = Path(caminho)
        if not sessao.is_absolute():
            sessao = ROOT / sessao
        return sessao

    sessoes = sorted(
        pasta
        for pasta in DEMONSTRACOES.glob("*")
        if pasta.is_dir()
    )

    if not sessoes:
        raise FileNotFoundError(
            "Nenhuma sessao em demonstracoes/."
        )

    return sessoes[-1]


def exemplos_evento(
    pasta_evento: Path,
) -> list[tuple[np.ndarray, float]]:
    exemplos = []

    antes = sorted(
        pasta_evento.glob("antes_*.png")
    )

    if antes:
        quantidade = max(
            1,
            min(2, len(antes) // 3),
        )

        negativos = antes[:quantidade]
        positivos = antes[-quantidade:]

        for caminho in negativos:
            frame = cv2.imread(str(caminho))
            if frame is None:
                continue

            exemplos.append(
                (
                    extrair_caracteristicas(frame),
                    0.0,
                )
            )

        for caminho in positivos:
            if caminho in negativos:
                continue

            frame = cv2.imread(str(caminho))
            if frame is None:
                continue

            exemplos.append(
                (
                    extrair_caracteristicas(frame),
                    1.0,
                )
            )

    acao = cv2.imread(
        str(pasta_evento / "acao.png")
    )
    if acao is not None:
        exemplos.append(
            (
                extrair_caracteristicas(acao),
                1.0,
            )
        )

    return exemplos


def montar_conjunto(
    eventos: list[Path],
) -> tuple[np.ndarray, np.ndarray]:
    xs = []
    ys = []

    for evento in eventos:
        for x, y in exemplos_evento(evento):
            xs.append(x[0])
            ys.append(y)

    if not xs:
        raise ValueError(
            "Nenhum exemplo valido encontrado."
        )

    return (
        np.asarray(xs, dtype=np.float32),
        np.asarray(ys, dtype=np.float32),
    )


def metricas(
    verdade: np.ndarray,
    previsto: np.ndarray,
) -> tuple[float, float, float, float]:
    verdade = verdade.astype(int)
    previsto = previsto.astype(int)

    tp = int(
        np.sum(
            (verdade == 1)
            & (previsto == 1)
        )
    )
    fp = int(
        np.sum(
            (verdade == 0)
            & (previsto == 1)
        )
    )
    fn = int(
        np.sum(
            (verdade == 1)
            & (previsto == 0)
        )
    )

    acuracia = float(
        np.mean(verdade == previsto)
    )
    precisao = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )
    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )
    f1 = (
        2 * precisao * recall
        / (precisao + recall)
        if precisao + recall
        else 0.0
    )

    return acuracia, precisao, recall, f1


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cria o primeiro modelo de imitacao "
            "do pulo a partir do modo professor."
        )
    )
    parser.add_argument(
        "--sessao",
        default=None,
        help=(
            "Pasta da sessao. Se omitido, usa "
            "a mais recente."
        ),
    )
    parser.add_argument(
        "--saida",
        default=str(MODELO),
    )
    args = parser.parse_args()

    sessao = encontrar_sessao(
        args.sessao
    )

    eventos = sorted(
        pasta
        for pasta in sessao.glob(
            "evento_*_pular"
        )
        if pasta.is_dir()
    )

    if len(eventos) < 10:
        print(
            "Poucas demonstracoes de pulo: "
            f"{len(eventos)}. Grave pelo menos 10."
        )
        return

    val_eventos = [
        evento
        for indice, evento in enumerate(eventos)
        if indice % 5 == 0
    ]
    treino_eventos = [
        evento
        for indice, evento in enumerate(eventos)
        if indice % 5 != 0
    ]

    treino_x, treino_y = montar_conjunto(
        treino_eventos
    )
    val_x, val_y = montar_conjunto(
        val_eventos
    )

    knn = criar_knn(
        treino_x,
        treino_y,
    )

    previstos = []

    for amostra in val_x:
        classe, _ = prever(
            knn,
            amostra.reshape(1, -1),
        )
        previstos.append(classe)

    previstos = np.asarray(previstos)

    acc, prec, rec, f1 = metricas(
        val_y,
        previstos,
    )

    proporcao_positiva = float(
        np.mean(val_y == 1)
    )
    baseline_maioria = max(
        proporcao_positiva,
        1.0 - proporcao_positiva,
    )

    todos_x, todos_y = montar_conjunto(
        eventos
    )

    salvar_dataset_modelo(
        args.saida,
        todos_x,
        todos_y,
    )

    print("SlayerAI - Aprendizado de pulo")
    print("=" * 40)
    print(f"Sessao: {sessao}")
    print(f"Eventos de pulo: {len(eventos)}")
    print(
        f"Treino por eventos: "
        f"{len(treino_eventos)}"
    )
    print(
        f"Validacao por eventos: "
        f"{len(val_eventos)}"
    )
    print(
        f"Amostras treino: {len(treino_y)} "
        f"(pular={int(np.sum(treino_y == 1))}, "
        f"esperar={int(np.sum(treino_y == 0))})"
    )
    print(
        f"Amostras validacao: {len(val_y)} "
        f"(pular={int(np.sum(val_y == 1))}, "
        f"esperar={int(np.sum(val_y == 0))})"
    )
    print("")
    print("Validacao temporal:")
    print(
        f"Baseline classe majoritaria: "
        f"{baseline_maioria:.3f}"
    )
    print(f"Acuracia: {acc:.3f}")
    print(f"Precisao pulo: {prec:.3f}")
    print(f"Recall pulo: {rec:.3f}")
    print(f"F1 pulo: {f1:.3f}")
    print("")
    print(
        "Rotulagem: frames antigos antes do clique = "
        "ESPERAR; ultimos frames antes do clique + "
        "frame da acao = PULAR."
    )
    print(
        f"Modelo de exemplos salvo em: "
        f"{args.saida}"
    )
    print(
        "Proximo passo: comparar essas metricas "
        "antes do dry-run ao vivo."
    )


if __name__ == "__main__":
    main()
