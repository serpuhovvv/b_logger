from typing import Optional
import yaml
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from b_logger.utils.paths import pathfinder


class BLoggerConfig:
    _instance: Optional["BLoggerConfig"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get(cls) -> "BLoggerConfig":
        if cls._instance is None:
            cls._instance = BLoggerConfig()
        return cls._instance

    def __init__(self, path: str = f'{pathfinder.project_root()}/blog.config.yaml'):
        self._extra = {}

        config_path = Path(path)
        self._data = self._load_config_file(config_path)

        # YAML
        self.project_name: Optional[str] = self._data.get("project_name")
        self.env: Optional[str] = self._data.get("env")
        self.base_url: Optional[str] = self._data.get("base_url")

        tz_value = self._data.get("tz", "UTC")
        self.tz: Optional[ZoneInfo] = self._process_tz(tz_value)

        self.integrations: Optional[dict] = self._data.get("integrations", {})
        self.qase: bool = bool(self.integrations.get("qase", False))
        self.allure: bool = bool(self.integrations.get("allure", False))

        # Other
        self._extra = {
            k: v for k, v in self._data.items()
            if not hasattr(self, k)
        }

    @staticmethod
    def _process_tz(tz_value):
        try:
            return ZoneInfo(tz_value)
        except ZoneInfoNotFoundError as e:
            raise RuntimeError(
                f"[BLogger] Timezone '{tz_value}' not found. Set a valid IANA timezone (e.g. 'UTC', 'Europe/Moscow', 'America/New_York')."
            ) from e

    @staticmethod
    def _load_config_file(path: Path = None) -> dict:
        if not path.exists():
            raise FileNotFoundError(f'[BLogger][ERROR] blog.config.yaml file not found: {path}')
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def apply_cli_options(self, config):
        for opt_name in config.option.__dict__:
            if opt_name.startswith("blog_"):
                value = getattr(config.option, opt_name)
                if value is not None:
                    field_name = opt_name.replace("blog_", "")
                    setattr(self, field_name, value)

    def __getitem__(self, key: str):
        return getattr(self, key, self._extra.get(key, None))

    def __setitem__(self, key: str, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self._extra[key] = value

    def __getattr__(self, key):
        if key in self._extra:
            return self._extra[key]
        print(f'[BLogger][WARN] blog_config object has no attribute "{key}"')

    def __setattr__(self, key, value):
        if key in {
            "_data", "_extra",
            "project_name", "tz",
            "env", "base_url",
            "qase", "allure"
        }:
            object.__setattr__(self, key, value)
        else:
            self._extra[key] = value

    def as_dict(self) -> dict:
        base = {
            "project_name": self.project_name,
            "tz": self.tz,
            "env": self.env,
            "base_url": self.base_url,
            "allure": self.allure,
            "qase": self.qase
        }
        return {**base, **self._extra}

    def __repr__(self):
        return f"<BLoggerConfig {self.as_dict()}>"


blog_config = BLoggerConfig.get()
