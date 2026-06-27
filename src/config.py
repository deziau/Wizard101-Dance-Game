import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
DEFAULT_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


@dataclass
class CaptureRegion:
    x: int = 0
    y: int = 0
    width: int = 800
    height: int = 150


@dataclass
class Config:
    capture_region: CaptureRegion = field(default_factory=CaptureRegion)
    threshold: float = 0.75
    auto_delay_ms: int = 50
    auto_input_interval_ms: int = 200
    template_dir: str = DEFAULT_TEMPLATE_DIR
    debug: bool = False

    @property
    def template_paths(self) -> dict[str, str]:
        return {
            d: os.path.join(self.template_dir, f"{d}.png")
            for d in ("up", "down", "left", "right")
        }

    def templates_exist(self) -> bool:
        return all(os.path.exists(p) for p in self.template_paths.values())

    def save(self, path: Optional[str] = None):
        path = path or DEFAULT_CONFIG_PATH
        data = asdict(self)
        data.pop("debug", None)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        path = path or DEFAULT_CONFIG_PATH
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        region_data = data.pop("capture_region", {})
        region = CaptureRegion(**region_data)
        data.pop("debug", None)
        data.pop("hit_zone_x", None)
        return cls(capture_region=region, **data)
