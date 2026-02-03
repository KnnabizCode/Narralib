import json
import os
from pathlib import Path
from typing import Any, Optional

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config_dir = Path.home() / ".narralib"
        self.config_file = self.config_dir / "config.json"
        self.config = {}
        self._load_config()

    def _load_config(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {}

    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self._save_config()
