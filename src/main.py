import argparse
import sys
import time

import cv2

from src.config import Config
from src.capture import ScreenCapture
from src.detector import ArrowDetector
from src.tracker import SequenceTracker
from src.output import DisplayOutput, AutoPlayOutput
from src.calibrate import run_calibration, run_capture_mode


def parse_args():
    parser = argparse.ArgumentParser(
        description="Wizard101 Dance Game Arrow Detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.main --calibrate       Run calibration wizard\n"
            "  python -m src.main --mode display     Show arrows in overlay\n"
            "  python -m src.main --mode auto        Auto-press arrow keys\n"
            "  python -m src.main --mode auto --debug Show detection debug window\n"
        ),
    )
    parser.add_argument(
        "--capture", action="store_true",
        help="Start screenshot capture mode (press F8 during gameplay to save screenshots)",
    )
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Run the calibration wizard using a saved or live screenshot",
    )
    parser.add_argument(
        "--mode", choices=["display", "auto"], default="display",
        help="Output mode: 'display' shows arrows in overlay, 'auto' presses keys (default: display)",
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to config.json (default: config.json in project root)",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Show a debug window with detection rectangles overlaid on capture",
    )
    parser.add_argument(
        "--threshold", type=float, default=None,
        help="Override detection confidence threshold (0.0-1.0)",
    )
    return parser.parse_args()


def run_main_loop(config: Config, mode: str, debug: bool):
    if not config.templates_exist():
        print("Error: Arrow template images not found.")
        print("Run with --calibrate first to set up templates.")
        sys.exit(1)

    capture = ScreenCapture(config.capture_region)
    detector = ArrowDetector(config.template_paths, config.threshold)
    tracker = SequenceTracker(config.hit_zone_x)

    if mode == "auto":
        output = AutoPlayOutput(delay_ms=config.auto_delay_ms)
        output.set_status("[F9] Toggle Auto  |  [F10] Quit  |  Mode: AUTO")
    else:
        output = DisplayOutput()
        output.set_status("[F10] Quit  |  Mode: DISPLAY")

    from pynput import keyboard

    running = True

    def on_f9():
        nonlocal output
        if mode == "auto" and isinstance(output, AutoPlayOutput):
            enabled = output.toggle()
            state = "ON" if enabled else "OFF"
            output.set_status(f"[F9] Toggle Auto  |  [F10] Quit  |  Auto: {state}")

    def on_f10():
        nonlocal running
        running = False

    hotkeys = keyboard.GlobalHotKeys({
        "<f9>": on_f9,
        "<f10>": on_f10,
    })
    hotkeys.start()

    target_fps = 20
    frame_time = 1.0 / target_fps

    print(f"Dance Game Helper started in {mode.upper()} mode.")
    print("Press F10 to quit.")
    if mode == "auto":
        print("Press F9 to toggle auto-play on/off.")

    try:
        while running:
            loop_start = time.time()

            frame = capture.grab_frame()
            detections = detector.detect(frame)
            tracker.update(detections, loop_start)

            upcoming = tracker.get_upcoming_sequence()
            output.show(upcoming)

            for arrow in tracker.get_hit_zone_arrows():
                output.on_action(arrow)

            if debug:
                debug_frame = frame.copy()
                for det in detections:
                    color = {
                        "up": (0, 0, 255),
                        "down": (255, 128, 0),
                        "left": (0, 255, 0),
                        "right": (0, 165, 255),
                    }.get(det.direction, (255, 255, 255))
                    cv2.rectangle(
                        debug_frame,
                        (det.x, det.y),
                        (det.x + det.width, det.y + det.height),
                        color, 2,
                    )
                    cv2.putText(
                        debug_frame,
                        f"{det.direction} {det.confidence:.2f}",
                        (det.x, det.y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1,
                    )
                cv2.line(
                    debug_frame,
                    (config.hit_zone_x, 0),
                    (config.hit_zone_x, debug_frame.shape[0]),
                    (0, 255, 255), 2,
                )
                cv2.imshow("Debug - Arrow Detection", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    running = False

            output.pump()

            elapsed = time.time() - loop_start
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        hotkeys.stop()
        output.destroy()
        capture.close()
        if debug:
            cv2.destroyAllWindows()
        print("Dance Game Helper stopped.")


def main():
    args = parse_args()
    config = Config.load(args.config)

    if args.threshold is not None:
        config.threshold = args.threshold
    config.debug = args.debug

    if args.capture:
        run_capture_mode()
        return

    if args.calibrate:
        config = run_calibration(config)
        return

    run_main_loop(config, args.mode, args.debug)


if __name__ == "__main__":
    main()
