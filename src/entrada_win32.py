import time


class EntradaWin32:
    """
    Envia uma tecla diretamente para a janela do Idle Slayer
    usando mensagens do Windows, sem precisar focar a janela.

    A validacao real com o jogo deve ser feita no PC de casa.
    """

    def __init__(
        self,
        titulo: str = "Idle Slayer",
        duracao_pressao: float = 0.03,
    ):
        if duracao_pressao < 0:
            raise ValueError(
                "duracao_pressao nao pode ser negativa."
            )

        self.titulo = titulo
        self.duracao_pressao = duracao_pressao

    def _resolver_janela(self) -> int:
        import win32gui

        hwnd = win32gui.FindWindow(
            None,
            self.titulo,
        )

        if not hwnd:
            raise RuntimeError(
                f'Janela "{self.titulo}" nao encontrada.'
            )

        return hwnd

    def pressionar(self, codigo_tecla: int) -> None:
        import win32con
        import win32gui

        hwnd = self._resolver_janela()

        win32gui.PostMessage(
            hwnd,
            win32con.WM_KEYDOWN,
            codigo_tecla,
            0,
        )

        if self.duracao_pressao > 0:
            time.sleep(self.duracao_pressao)

        win32gui.PostMessage(
            hwnd,
            win32con.WM_KEYUP,
            codigo_tecla,
            0,
        )
