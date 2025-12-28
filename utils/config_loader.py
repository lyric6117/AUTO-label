import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        if self._config is not None:
            return self._config

        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        self._validate_config()
        return self._config

    def _validate_config(self):
        required_keys = ['decision', 'model', 'storage', 'api']
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required config key: {key}")

        decision = self._config['decision']
        if 'auto_accept_threshold' not in decision:
            raise ValueError("Missing auto_accept_threshold in decision config")
        if 'review_min_threshold' not in decision:
            raise ValueError("Missing review_min_threshold in decision config")

    def get(self, key: str, default=None):
        if self._config is None:
            self.load_config()
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def decision(self) -> Dict[str, Any]:
        return self.get('decision', {})

    @property
    def model(self) -> Dict[str, Any]:
        return self.get('model', {})

    @property
    def storage(self) -> Dict[str, Any]:
        return self.get('storage', {})

    @property
    def api(self) -> Dict[str, Any]:
        return self.get('api', {})

    @property
    def inference(self) -> Dict[str, Any]:
        return self.get('inference', {})

    @property
    def logging(self) -> Dict[str, Any]:
        return self.get('logging', {})


def get_config() -> ConfigLoader:
    return ConfigLoader()
