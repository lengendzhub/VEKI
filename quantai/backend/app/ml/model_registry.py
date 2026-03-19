# backend/app/ml/model_registry.py
from __future__ import annotations

import json
from pathlib import Path


class ModelRegistry:
    def __init__(self, models_dir: str = "./models") -> None:
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def save_meta(self, version: str, meta: dict) -> None:
        target = self.models_dir / version
        target.mkdir(parents=True, exist_ok=True)
        (target / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def load_meta(self, version: str) -> dict:
        path = self.models_dir / version / "meta.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def set_active_version(self, version: str) -> None:
        (self.models_dir / "ACTIVE").write_text(version, encoding="utf-8")

    def get_active_version(self) -> str:
        active = self.models_dir / "ACTIVE"
        return active.read_text(encoding="utf-8").strip() if active.exists() else "untrained"
