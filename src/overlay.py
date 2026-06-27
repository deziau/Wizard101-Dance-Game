import tkinter as tk
from tkinter import font as tkfont

ARROW_SYMBOLS = {
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
}


class ArrowOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dance Helper")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("500x100+10+10")
        self.root.resizable(True, False)

        self._phase_label = tk.Label(
            self.root,
            text="IDLE",
            bg="#16213e",
            fg="#888888",
            anchor="w",
            padx=10,
            pady=2,
        )
        self._phase_label.pack(fill=tk.X)

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
        fnt = tkfont.Font(family="Consolas", size=22, weight="bold")
        self._label.configure(font=fnt)

    def show_sequence(self, sequence: list[str], phase: str, input_index: int = 0) -> None:
        self._phase_label.configure(text=phase.upper())

        if not sequence:
            self._label.configure(text="Waiting for arrows...", fg="#e0e0e0")
            return

        symbols = [ARROW_SYMBOLS.get(d, "?") for d in sequence]
        text = "  ".join(symbols)
        self._label.configure(text=text)

        if phase == "recording":
            self._label.configure(fg="#FFFF44")
            self._phase_label.configure(text=f"RECORDING... ({len(sequence)} arrows)", fg="#FFFF44")
        elif phase == "ready":
            self._label.configure(fg="#44FF44")
            self._phase_label.configure(text=f"SEQUENCE READY ({len(sequence)} arrows) - enter them now!", fg="#44FF44")
        elif phase == "inputting":
            self._label.configure(fg="#44AAFF")
            self._phase_label.configure(text=f"AUTO-INPUT {input_index}/{len(sequence)}", fg="#44AAFF")
        else:
            self._label.configure(fg="#e0e0e0")

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
