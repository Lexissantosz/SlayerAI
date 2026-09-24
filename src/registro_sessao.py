import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from decisor import Decisao
from estado_jogo import EstadoJogo
from percepcao import DeteccaoObjeto


@dataclass(frozen=True)
class RegistroSessao:
    frame: int
    timestamp: str
    largura: int
    altura: int
    deteccoes: list[dict]
    decisao: dict


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def criar_registro(
    frame: int,
    estado: EstadoJogo,
    decisao: Decisao,
) -> RegistroSessao:
    deteccoes = [
        {
            "tipo": objeto.tipo.value,
            "caixa": [
                objeto.caixa.x1,
                objeto.caixa.y1,
                objeto.caixa.x2,
                objeto.caixa.y2,
            ],
            "confianca": objeto.confianca,
        }
        for objeto in estado.objetos
    ]

    return RegistroSessao(
        frame=frame,
        timestamp=_agora_iso(),
        largura=estado.largura,
        altura=estado.altura,
        deteccoes=deteccoes,
        decisao={
            "acao": decisao.acao.value,
            "motivo": decisao.motivo,
        },
    )


class GravadorSessao:
    def __init__(
        self,
        caminho: str | Path,
    ):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def registrar(
        self,
        frame: int,
        estado: EstadoJogo,
        decisao: Decisao,
    ) -> None:
        registro = criar_registro(
            frame=frame,
            estado=estado,
            decisao=decisao,
        )

        with self.caminho.open(
            "a",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                asdict(registro),
                arquivo,
                ensure_ascii=False,
            )
            arquivo.write("\n")


def deteccoes_do_registro(
    registro: dict,
) -> list[DeteccaoObjeto]:
    from estado_jogo import TipoObjeto

    deteccoes = []

    for item in registro.get("deteccoes", []):
        caixa = tuple(
            int(valor)
            for valor in item["caixa"]
        )

        deteccoes.append(
            DeteccaoObjeto(
                tipo=TipoObjeto(item["tipo"]),
                caixa=caixa,
                confianca=float(
                    item.get(
                        "confianca",
                        1.0,
                    )
                ),
            )
        )

    return deteccoes


def carregar_registros(
    caminho: str | Path,
) -> list[dict]:
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Sessao nao encontrada: {caminho}"
        )

    registros = []

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        for numero_linha, linha in enumerate(
            arquivo,
            start=1,
        ):
            linha = linha.strip()

            if not linha:
                continue

            try:
                registros.append(
                    json.loads(linha)
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "JSON invalido na linha "
                    f"{numero_linha}: {exc.msg}"
                ) from exc

    return registros
