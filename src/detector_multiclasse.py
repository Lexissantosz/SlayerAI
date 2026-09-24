import time
from dataclasses import dataclass
from pathlib import Path

from ultralytics import YOLO

from estado_jogo import TipoObjeto
from percepcao import DeteccaoObjeto


CLASSES_V02 = {
    0: TipoObjeto.PLAYER,
    1: TipoObjeto.INIMIGO,
}


@dataclass(frozen=True)
class ResultadoDeteccaoMulticlasse:
    deteccoes: list[DeteccaoObjeto]
    inferencia_ms: float


class DetectorMulticlasse:
    def __init__(
        self,
        modelo: str | Path,
        conf: float = 0.30,
        imgsz: int = 320,
        device: str = "cpu",
    ):
        self.caminho_modelo = Path(modelo)

        if not self.caminho_modelo.exists():
            raise FileNotFoundError(
                "Modelo nao encontrado: "
                f"{self.caminho_modelo}"
            )

        if not 0 < conf <= 1:
            raise ValueError(
                "conf deve estar entre 0 e 1."
            )

        if imgsz < 64:
            raise ValueError(
                "imgsz deve ser pelo menos 64."
            )

        self.conf = conf
        self.imgsz = imgsz
        self.device = device
        self.modelo = YOLO(
            str(self.caminho_modelo)
        )

    def detectar(
        self,
        frame,
    ) -> ResultadoDeteccaoMulticlasse:
        inicio = time.perf_counter()

        resultados = self.modelo.predict(
            source=frame,
            conf=self.conf,
            imgsz=self.imgsz,
            verbose=False,
            device=self.device,
        )

        inferencia_ms = (
            time.perf_counter() - inicio
        ) * 1000.0

        deteccoes: list[DeteccaoObjeto] = []

        if not resultados:
            return ResultadoDeteccaoMulticlasse(
                deteccoes=deteccoes,
                inferencia_ms=inferencia_ms,
            )

        altura, largura = frame.shape[:2]

        for caixa in resultados[0].boxes:
            classe_id = int(
                caixa.cls[0].item()
            )
            tipo = CLASSES_V02.get(
                classe_id,
                TipoObjeto.DESCONHECIDO,
            )

            coords = (
                caixa.xyxy[0]
                .cpu()
                .numpy()
                .astype(int)
                .tolist()
            )

            x1 = max(
                0,
                min(coords[0], largura - 1),
            )
            y1 = max(
                0,
                min(coords[1], altura - 1),
            )
            x2 = max(
                x1 + 1,
                min(coords[2], largura),
            )
            y2 = max(
                y1 + 1,
                min(coords[3], altura),
            )

            deteccoes.append(
                DeteccaoObjeto(
                    tipo=tipo,
                    caixa=(x1, y1, x2, y2),
                    confianca=float(
                        caixa.conf[0].item()
                    ),
                )
            )

        return ResultadoDeteccaoMulticlasse(
            deteccoes=deteccoes,
            inferencia_ms=inferencia_ms,
        )
