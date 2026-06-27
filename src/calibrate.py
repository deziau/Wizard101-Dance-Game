import os
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
import mss

from src.config import Config, CaptureRegion


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


def take_screenshot() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        frame = np.array(img)
        return frame[:, :, :3]


def run_calibration(config: Config) -> Config:
    master = tk.Tk()
    master.withdraw()

    messagebox.showinfo(
        "Calibration - Step 1",
        "Open Wizard101 and start a dance game.\n\n"
        "Make sure arrows are visible on screen, then click OK.\n\n"
        "A screenshot will be taken."
    )

    screenshot = take_screenshot()

    messagebox.showinfo(
        "Calibration - Step 2",
        "Draw a rectangle around the area where arrows scroll.\n\n"
        "Click and drag from top-left to bottom-right."
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
        "Calibration - Step 3",
        "Click on the hit zone position — the spot where\n"
        "you need to press the arrow key.\n\n"
        "Click on the left side where the arrow target is."
    )
    point_sel = PointSelector(screenshot, config.capture_region, "Click the hit zone position")
    hit_x = point_sel.run()
    if hit_x is not None:
        config.hit_zone_x = hit_x

    os.makedirs(config.template_dir, exist_ok=True)

    for direction in ("up", "down", "left", "right"):
        messagebox.showinfo(
            f"Calibration - {direction.upper()} Arrow",
            f"Draw a tight box around one {direction.upper()} arrow."
        )
        tmpl_sel = RegionSelector(screenshot, f"Select {direction.upper()} arrow")
        tmpl_result = tmpl_sel.run()
        if tmpl_result is None:
            messagebox.showwarning("Skipped", f"No {direction} arrow selected.")
            continue
        tx, ty, tw, th = tmpl_result
        cropped = screenshot[ty:ty + th, tx:tx + tw]
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        path = os.path.join(config.template_dir, f"{direction}.png")
        cv2.imwrite(path, gray)

    config.save()
    messagebox.showinfo("Done", "Calibration complete!\n\nConfig saved to config.json.")
    master.destroy()
    return config
