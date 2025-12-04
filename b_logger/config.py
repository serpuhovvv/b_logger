from typing import Optional
import yaml
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from b_logger.utils.paths import pathfinder


class BLoggerConfig:
    _instance: Optional["BLoggerConfig"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get(cls) -> "BLoggerConfig":
        if cls._instance is None:
            cls._instance = BLoggerConfig()
        return cls._instance

    def __init__(
        self,
        config_path: str = f"{pathfinder.project_root()}/blog.config.yaml",
        notes_path: str = f"{pathfinder.project_root()}/blog.notes.yaml",
    ):
        if self._initialized:
            return

        self._data = self._load_config_file(config_path)

        # blog.config.yaml
        self.project_name: Optional[str] = self._data.get("project_name")
        self.env: Optional[str] = self._data.get("env", None)
        self.base_url: Optional[str] = self._data.get("base_url", None)

        tz_value = self._data.get("tz", "UTC")
        self.tz: Optional[ZoneInfo] = self._process_tz(tz_value)

        self.integrations: dict = self._data.get("integrations", {}) or {}
        self.qase: bool = bool(self.integrations.get("qase", False))
        self.allure: bool = bool(self.integrations.get("allure", False))

        self.hide_passwords: bool = bool(self._data.get("hide_passwords", True))

        # blog.notes.yaml
        self.notes: dict = self._load_notes_file(notes_path) or {}

        self._initialized = True

    @staticmethod
    def _load_config_file(path: str = None) -> dict:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'[BLogger][ERROR] blog.config.yaml file not found: {path}')

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def _load_notes_file(path: str = None) -> dict:
        path = Path(path)
        if not path.exists():
            # print(f'[BLogger][WARN] blog.notes.yaml file not found: {path}')
            return {}

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def _process_tz(tz_value):
        try:
            return ZoneInfo(tz_value)
        except ZoneInfoNotFoundError as e:
            raise RuntimeError(
                f'[BLogger] Timezone "{tz_value}" not found. '
                f'Set a valid IANA timezone (e.g. "UTC", "Europe/Moscow", "America/New_York").'
            ) from e

    def apply_cli_options(self, config):
        for opt_name in config.option.__dict__:
            if opt_name.startswith("blog_"):
                value = getattr(config.option, opt_name)
                if value is not None:
                    field_name = opt_name.replace("blog_", "")
                    setattr(self, field_name, value)

    def __getitem__(self, key: str):
        return getattr(self, key, None)

    def __setitem__(self, key: str, value):
        setattr(self, key, value)

    def as_dict(self) -> dict:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    def __repr__(self):
        return f'<BLoggerConfig {self.as_dict()}>'


blog_config = BLoggerConfig.get()
