import ctypes

import cv2
import numpy as np
import win32gui
import win32ui


class IdleSlayerNaoEncontrado(RuntimeError):
    pass


class CapturaIndisponivel(RuntimeError):
    pass


class IdleSlayerCapture:
    """Captura a area cliente do Idle Slayer diretamente pela janela do Windows."""

    def __init__(self, titulo: str = "Idle Slayer"):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

        self.titulo = titulo
        self.hwnd = 0
        self.hwnd_dc = None
        self.mfc_dc = None
        self.save_dc = None
        self.bitmap = None
        self.largura = 0
        self.altura = 0

        self.conectar()

    def conectar(self) -> None:
        self.hwnd = win32gui.FindWindow(None, self.titulo)

        if self.hwnd == 0:
            raise IdleSlayerNaoEncontrado(
                f'Janela "{self.titulo}" nao encontrada.'
            )

    def esta_aberto(self) -> bool:
        return bool(self.hwnd and win32gui.IsWindow(self.hwnd))

    def _tamanho_atual(self) -> tuple[int, int]:
        if not self.esta_aberto():
            raise IdleSlayerNaoEncontrado("Idle Slayer foi fechado.")

        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        largura = right - left
        altura = bottom - top

        if largura <= 0 or altura <= 0:
            raise CapturaIndisponivel(
                "Idle Slayer esta sem area capturavel. "
                "Restaure ou abra a janela do jogo."
            )

        return largura, altura

    def _liberar_recursos(self) -> None:
        if self.bitmap is not None:
            try:
                win32gui.DeleteObject(self.bitmap.GetHandle())
            except Exception:
                pass

        if self.save_dc is not None:
            try:
                self.save_dc.DeleteDC()
            except Exception:
                pass

        if self.mfc_dc is not None:
            try:
                self.mfc_dc.DeleteDC()
            except Exception:
                pass

        if self.hwnd_dc is not None and self.hwnd:
            try:
                win32gui.ReleaseDC(self.hwnd, self.hwnd_dc)
            except Exception:
                pass

        self.hwnd_dc = None
        self.mfc_dc = None
        self.save_dc = None
        self.bitmap = None
        self.largura = 0
        self.altura = 0

    def _preparar_recursos(self, largura: int, altura: int) -> None:
        self._liberar_recursos()

        self.hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        self.mfc_dc = win32ui.CreateDCFromHandle(self.hwnd_dc)
        self.save_dc = self.mfc_dc.CreateCompatibleDC()

        self.bitmap = win32ui.CreateBitmap()
        self.bitmap.CreateCompatibleBitmap(
            self.mfc_dc,
            largura,
            altura,
        )
        self.save_dc.SelectObject(self.bitmap)

        self.largura = largura
        self.altura = altura

    def capturar(self) -> np.ndarray:
        largura, altura = self._tamanho_atual()

        if (
            self.bitmap is None
            or largura != self.largura
            or altura != self.altura
        ):
            self._preparar_recursos(largura, altura)

        resultado = ctypes.windll.user32.PrintWindow(
            self.hwnd,
            self.save_dc.GetSafeHdc(),
            3,
        )

        if resultado != 1:
            raise CapturaIndisponivel(
                "O Windows nao conseguiu capturar a janela do Idle Slayer."
            )

        bmpinfo = self.bitmap.GetInfo()
        bmpstr = self.bitmap.GetBitmapBits(True)

        frame = np.frombuffer(bmpstr, dtype=np.uint8)
        frame = frame.reshape(
            (
                bmpinfo["bmHeight"],
                bmpinfo["bmWidth"],
                4,
            )
        )

        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def close(self) -> None:
        self._liberar_recursos()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
