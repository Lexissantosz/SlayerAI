import argparse

from decisor import DecisorBasico
from executor import ExecutorSimulado
from pipeline import CicloSlayerAI
from registro_sessao import (
    carregar_registros,
    deteccoes_do_registro,
)


def reproduzir(
    caminho: str,
) -> tuple[int, int]:
    registros = carregar_registros(caminho)

    executor = ExecutorSimulado()
    ciclo = CicloSlayerAI(
        DecisorBasico(),
        executor,
    )

    divergencias = 0

    for registro in registros:
        resultado = ciclo.processar_deteccoes(
            largura=int(registro["largura"]),
            altura=int(registro["altura"]),
            deteccoes=deteccoes_do_registro(
                registro
            ),
        )

        esperado = (
            registro
            .get("decisao", {})
            .get("acao")
        )

        atual = resultado.decisao.acao.value

        if esperado is not None and esperado != atual:
            divergencias += 1
            status = "DIVERGIU"
        else:
            status = "OK"

        print(
            f"frame {registro['frame']:>4}: "
            f"{atual:<8} | {status}"
        )

    return len(registros), divergencias


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduz uma sessao JSONL sem abrir "
            "o Idle Slayer."
        )
    )
    parser.add_argument(
        "sessao",
        help="Arquivo .jsonl registrado pelo SlayerAI.",
    )
    args = parser.parse_args()

    total, divergencias = reproduzir(
        args.sessao
    )

    print("")
    print(f"Frames reproduzidos: {total}")
    print(f"Divergencias: {divergencias}")


if __name__ == "__main__":
    main()
