import time
from pathlib import Path

from ultralytics import YOLO

from tipos_visao import Deteccao
from visao_utils import (
    ROI,
    calcular_roi_pixels,
    suavizar_caixa,
)


class DetectorPlayer:
    def __init__(
        self,
        modelo: str | Path,
        conf: float = 0.35,
        imgsz: int = 320,
        device: str = "cpu",
        roi: ROI | None = None,
        suavizacao: float = 1.0,
    ):
        self.caminho_modelo = Path(modelo)

        if not self.caminho_modelo.exists():
            raise FileNotFoundError(
                f"Modelo nao encontrado: {self.caminho_modelo}"
            )

        if not 0 < conf <= 1:
            raise ValueError("conf deve estar entre 0 e 1.")

        if imgsz < 64:
            raise ValueError("imgsz deve ser pelo menos 64.")

        if not 0 <= suavizacao <= 1:
            raise ValueError("suavizacao deve estar entre 0 e 1.")

        self.conf = conf
        self.imgsz = imgsz
        self.device = device
        self.roi = roi
        self.suavizacao = suavizacao
        self.modelo = YOLO(str(self.caminho_modelo))
        self.ultima_caixa = None

    def detectar(self, frame) -> Deteccao | None:
        altura_frame, largura_frame = frame.shape[:2]

        x1_roi, y1_roi, x2_roi, y2_roi = calcular_roi_pixels(
            largura_frame,
            altura_frame,
            self.roi,
        )

        entrada = frame[
            y1_roi:y2_roi,
            x1_roi:x2_roi,
        ]

        inicio = time.perf_counter()

        resultados = self.modelo.predict(
            source=entrada,
            conf=self.conf,
            imgsz=self.imgsz,
            verbose=False,
            device=self.device,
        )

        inferencia_ms = (
            time.perf_counter() - inicio
        ) * 1000.0

        if not resultados or len(resultados[0].boxes) == 0:
            self.ultima_caixa = None
            return None

        melhor = max(
            resultados[0].boxes,
            key=lambda caixa: float(caixa.conf[0].item()),
        )

        coords = (
            melhor.xyxy[0]
            .cpu()
            .numpy()
            .astype(int)
            .tolist()
        )

        caixa = (
            coords[0] + x1_roi,
            coords[1] + y1_roi,
            coords[2] + x1_roi,
            coords[3] + y1_roi,
        )

        caixa = suavizar_caixa(
            self.ultima_caixa,
            caixa,
            self.suavizacao,
        )
        self.ultima_caixa = caixa

        return Deteccao(
            caixa=caixa,
            confianca=float(melhor.conf[0].item()),
            inferencia_ms=inferencia_ms,
        )
