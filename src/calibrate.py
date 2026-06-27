import os
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
import mss

from src.config import Config, CaptureRegion

CAPTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "captures")

ROTATION_MAP = {
    "up": {
        "up": None,
        "right": cv2.ROTATE_90_CLOCKWISE,
        "down": cv2.ROTATE_180,
        "left": cv2.ROTATE_90_COUNTERCLOCKWISE,
    },
    "down": {
        "down": None,
        "left": cv2.ROTATE_90_CLOCKWISE,
        "up": cv2.ROTATE_180,
        "right": cv2.ROTATE_90_COUNTERCLOCKWISE,
    },
    "left": {
        "left": None,
        "up": cv2.ROTATE_90_CLOCKWISE,
        "right": cv2.ROTATE_180,
        "down": cv2.ROTATE_90_COUNTERCLOCKWISE,
    },
    "right": {
        "right": None,
        "down": cv2.ROTATE_90_CLOCKWISE,
        "left": cv2.ROTATE_180,
        "up": cv2.ROTATE_90_COUNTERCLOCKWISE,
    },
}


class RegionSelector:
    def __init__(self, screenshot: np.ndarray, title: str = "Select Region"):
        self.screenshot = screenshot
        self.title = title
        self.start = None
        self.end = None
        self.rect_id = None
        self.result = None

        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.attributes("-topmost", True)

        h, w = screenshot.shape[:2]
        scale = min(1.0, 1400 / w, 900 / h)
        self.scale = scale
        disp_w, disp_h = int(w * scale), int(h * scale)

        self.canvas = tk.Canvas(self.root, width=disp_w, height=disp_h, cursor="crosshair")
        self.canvas.pack()

        disp = cv2.resize(screenshot, (disp_w, disp_h))
        disp_rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        from PIL import Image, ImageTk
        self._img = ImageTk.PhotoImage(Image.fromarray(disp_rgb))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._img)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        label = tk.Label(self.root, text=title, bg="#222", fg="#fff", padx=10, pady=5)
        label.pack(fill=tk.X)

    def _on_press(self, event):
        self.start = (event.x, event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)

    def _on_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start[0], self.start[1], event.x, event.y,
            outline="#00FF00", width=2
        )

    def _on_release(self, event):
        self.end = (event.x, event.y)
        x1 = min(self.start[0], self.end[0])
        y1 = min(self.start[1], self.end[1])
        x2 = max(self.start[0], self.end[0])
        y2 = max(self.start[1], self.end[1])
        self.result = (
            int(x1 / self.scale),
            int(y1 / self.scale),
            int((x2 - x1) / self.scale),
            int((y2 - y1) / self.scale),
        )
        self.root.destroy()

    def run(self) -> tuple[int, int, int, int] | None:
        self.root.grab_set()
        self.root.wait_window()
        return self.result


class PointSelector:
    def __init__(self, screenshot: np.ndarray, region: CaptureRegion, title: str = "Click Hit Zone"):
        self.title = title
        self.result = None

        cropped = screenshot[
            region.y:region.y + region.height,
            region.x:region.x + region.width
        ]
        self.region = region

        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.attributes("-topmost", True)

        h, w = cropped.shape[:2]
        scale = min(1.0, 1400 / w, 600 / h)
        self.scale = scale
        disp_w, disp_h = int(w * scale), int(h * scale)

        self.canvas = tk.Canvas(self.root, width=disp_w, height=disp_h, cursor="crosshair")
        self.canvas.pack()

        disp = cv2.resize(cropped, (disp_w, disp_h))
        disp_rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        from PIL import Image, ImageTk
        self._img = ImageTk.PhotoImage(Image.fromarray(disp_rgb))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._img)

        self.canvas.bind("<ButtonPress-1>", self._on_click)

        label = tk.Label(self.root, text=title, bg="#222", fg="#fff", padx=10, pady=5)
        label.pack(fill=tk.X)

    def _on_click(self, event):
        self.result = int(event.x / self.scale)
        self.root.destroy()

    def run(self) -> int | None:
        self.root.grab_set()
        self.root.wait_window()
        return self.result


class DirectionPicker:
    def __init__(self):
        self.result = None

        self.root = tk.Toplevel()
        self.root.title("Which direction is this arrow?")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("350x200")
        self.root.resizable(False, False)

        label = tk.Label(
            self.root,
            text="Which direction is the arrow\nyou just selected?",
            bg="#1a1a2e", fg="#ffffff",
            font=("Consolas", 12),
            pady=15,
        )
        label.pack()

        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(expand=True)

        buttons = [
            ("UP", "up", 1, 0),
            ("DOWN", "down", 1, 2),
            ("LEFT", "left", 1, 1),
            ("RIGHT", "right", 1, 3),
        ]
        # Layout: top row = UP, middle row = LEFT RIGHT, bottom row = DOWN
        tk.Button(
            btn_frame, text="  UP  ", font=("Consolas", 14, "bold"),
            bg="#FF4444", fg="white", command=lambda: self._pick("up"),
        ).grid(row=0, column=1, padx=5, pady=3)
        tk.Button(
            btn_frame, text=" LEFT ", font=("Consolas", 14, "bold"),
            bg="#44FF44", fg="black", command=lambda: self._pick("left"),
        ).grid(row=1, column=0, padx=5, pady=3)
        tk.Button(
            btn_frame, text=" RIGHT", font=("Consolas", 14, "bold"),
            bg="#FFAA00", fg="black", command=lambda: self._pick("right"),
        ).grid(row=1, column=2, padx=5, pady=3)
        tk.Button(
            btn_frame, text=" DOWN ", font=("Consolas", 14, "bold"),
            bg="#44AAFF", fg="white", command=lambda: self._pick("down"),
        ).grid(row=2, column=1, padx=5, pady=3)

    def _pick(self, direction: str):
        self.result = direction
        self.root.destroy()

    def run(self) -> str | None:
        self.root.grab_set()
        self.root.wait_window()
        return self.result


def take_screenshot() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        frame = np.array(img)
        return frame[:, :, :3]


def generate_rotated_templates(arrow_img: np.ndarray, source_direction: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    rotations = ROTATION_MAP[source_direction]

    for target_dir, rotation_code in rotations.items():
        if rotation_code is None:
            rotated = arrow_img.copy()
        else:
            rotated = cv2.rotate(arrow_img, rotation_code)
        path = os.path.join(output_dir, f"{target_dir}.png")
        cv2.imwrite(path, rotated)


def run_capture_mode():
    os.makedirs(CAPTURES_DIR, exist_ok=True)

    print("Screenshot capture mode started.")
    print("Press F8 to save a screenshot during gameplay.")
    print("Press F10 to stop.")
    print(f"Screenshots will be saved to: {CAPTURES_DIR}")

    from pynput import keyboard

    running = True
    count = 0

    def on_f8():
        nonlocal count
        screenshot = take_screenshot()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        path = os.path.join(CAPTURES_DIR, filename)
        cv2.imwrite(path, screenshot)
        count += 1
        print(f"  Saved screenshot #{count}: {filename}")

    def on_f10():
        nonlocal running
        running = False

    hotkeys = keyboard.GlobalHotKeys({
        "<f8>": on_f8,
        "<f10>": on_f10,
    })
    hotkeys.start()

    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        hotkeys.stop()

    print(f"Capture mode stopped. {count} screenshot(s) saved.")


def _pick_screenshot(master: tk.Tk) -> np.ndarray | None:
    captures = []
    if os.path.isdir(CAPTURES_DIR):
        captures = sorted(
            [f for f in os.listdir(CAPTURES_DIR) if f.endswith(".png")],
            reverse=True,
        )

    if captures:
        choice = messagebox.askyesno(
            "Calibration",
            f"Found {len(captures)} saved screenshot(s) in captures/ folder.\n\n"
            "Use a saved screenshot?\n\n"
            "Yes = pick from saved screenshots\n"
            "No = take a new screenshot now",
        )
        if choice:
            picker = tk.Toplevel(master)
            picker.title("Pick a screenshot")
            picker.attributes("-topmost", True)
            picker.geometry("400x300")
            selected_path = [None]

            listbox = tk.Listbox(picker, font=("Consolas", 11))
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            for f in captures:
                listbox.insert(tk.END, f)
            listbox.selection_set(0)

            def on_select():
                idx = listbox.curselection()
                if idx:
                    selected_path[0] = os.path.join(CAPTURES_DIR, captures[idx[0]])
                picker.destroy()

            tk.Button(picker, text="Use This Screenshot", command=on_select,
                      font=("Consolas", 11), bg="#44AA44", fg="white").pack(pady=5)
            picker.grab_set()
            picker.wait_window()

            if selected_path[0]:
                img = cv2.imread(selected_path[0])
                if img is not None:
                    return img

    messagebox.showinfo(
        "Calibration",
        "Open Wizard101 and start a dance game.\n\n"
        "Make sure arrows are visible on screen, then click OK.\n\n"
        "A screenshot will be taken.",
    )
    return take_screenshot()


def run_calibration(config: Config) -> Config:
    master = tk.Tk()
    master.withdraw()

    screenshot = _pick_screenshot(master)
    if screenshot is None:
        messagebox.showerror("Error", "No screenshot available.")
        master.destroy()
        return config

    messagebox.showinfo(
        "Calibration - Scroll Region",
        "Draw a rectangle around the area where arrows scroll.\n\n"
        "Click and drag from top-left to bottom-right.",
    )
    selector = RegionSelector(screenshot, "Select the arrow scroll region")
    region_result = selector.run()
    if region_result is None:
        messagebox.showerror("Error", "No region selected.")
        master.destroy()
        return config

    x, y, w, h = region_result
    config.capture_region = CaptureRegion(x=x, y=y, width=w, height=h)

    messagebox.showinfo(
        "Calibration - Hit Zone",
        "Click on the hit zone position — the spot where\n"
        "you need to press the arrow key.\n\n"
        "Click on the left side where the arrow target is.",
    )
    point_sel = PointSelector(screenshot, config.capture_region, "Click the hit zone position")
    hit_x = point_sel.run()
    if hit_x is not None:
        config.hit_zone_x = hit_x

    messagebox.showinfo(
        "Calibration - Arrow Template",
        "Draw a tight box around ONE arrow (any direction).\n\n"
        "You only need to select ONE — the other 3 will be\n"
        "generated automatically by rotating it.",
    )
    tmpl_sel = RegionSelector(screenshot, "Select ONE arrow (any direction)")
    tmpl_result = tmpl_sel.run()
    if tmpl_result is None:
        messagebox.showerror("Error", "No arrow selected.")
        master.destroy()
        return config

    tx, ty, tw, th = tmpl_result
    cropped = screenshot[ty:ty + th, tx:tx + tw]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    dir_picker = DirectionPicker()
    source_direction = dir_picker.run()
    if source_direction is None:
        messagebox.showerror("Error", "No direction selected.")
        master.destroy()
        return config

    generate_rotated_templates(gray, source_direction, config.template_dir)

    config.save()
    messagebox.showinfo(
        "Done",
        f"Calibration complete!\n\n"
        f"Selected arrow: {source_direction.upper()}\n"
        f"Generated all 4 templates via rotation.\n\n"
        f"Config saved to config.json.",
    )
    master.destroy()
    return config
