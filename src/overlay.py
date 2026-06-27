import tkinter as tk
from tkinter import font as tkfont

ARROW_SYMBOLS = {
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
}

ARROW_COLORS = {
    "up": "#FF4444",
    "down": "#44AAFF",
    "left": "#44FF44",
    "right": "#FFAA00",
}


class ArrowOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dance Helper")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("400x80+10+10")
        self.root.resizable(True, False)

        self._label = tk.Label(
            self.root,
            text="Waiting for arrows...",
            bg="#1a1a2e",
            fg="#e0e0e0",
            anchor="w",
            padx=10,
            pady=5,
        )
        self._label.pack(fill=tk.BOTH, expand=True)
        self._update_font()

        self._status = tk.Label(
            self.root,
            text="[F9] Toggle  |  [F10] Quit",
            bg="#16213e",
            fg="#888888",
            anchor="center",
            padx=5,
            pady=2,
        )
        self._status.pack(fill=tk.X)

    def _update_font(self):
        fnt = tkfont.Font(family="Consolas", size=24, weight="bold")
        self._label.configure(font=fnt)

    def update_arrows(self, directions: list[str], raw_directions: list[str] | None = None) -> None:
        if directions:
            text = "  ".join(ARROW_SYMBOLS.get(d, "?") for d in directions)
            self._label.configure(text=text, fg="#FFFFFF")
        elif raw_directions:
            text = "  ".join(ARROW_SYMBOLS.get(d, "?") for d in raw_directions)
            self._label.configure(text=text, fg="#AAAAFF")
        else:
            self._label.configure(text="Waiting for arrows...", fg="#e0e0e0")

    def set_status(self, text: str) -> None:
        self._status.configure(text=text)

    def pump(self) -> None:
        self.root.update_idletasks()
        self.root.update()

    def destroy(self) -> None:
        try:
            self.root.destroy()
        except tk.TclError:
            pass
