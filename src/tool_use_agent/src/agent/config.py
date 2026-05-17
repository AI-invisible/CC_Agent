"""
Configuration management
"""
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

from .base import AgentConfig


class ConfigManager:
    """Configuration manager for agent"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config manager

        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "configs"
        self._configs: Dict[str, AgentConfig] = {}

    def load_config(self, name: str = "default", config_path: Optional[str] = None) -> AgentConfig:
        """
        Load configuration

        Args:
            name: Configuration name
            config_path: Optional custom config path

        Returns:
            AgentConfig: Loaded configuration
        """
        if config_path:
            config = AgentConfig.load_from_file(config_path)
        else:
            config_file = self.config_dir / f"{name}.yaml"
            if not config_file.exists():
                config_file = self.config_dir / f"{name}.json"

            if config_file.exists():
                config = AgentConfig.load_from_file(str(config_file))
            else:
                config = AgentConfig()  # Use default

        self._configs[name] = config
        return config

    def save_config(self, config: AgentConfig, name: str = "default") -> None:
        """
        Save configuration

        Args:
            config: Configuration to save
            name: Configuration name
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_path = self.config_dir / f"{name}.yaml"
        config.save_to_file(str(config_path))
        self._configs[name] = config

    def get_config(self, name: str = "default") -> Optional[AgentConfig]:
        """
        Get cached configuration

        Args:
            name: Configuration name

        Returns:
            AgentConfig: Cached configuration or None
        """
        return self._configs.get(name)

    @staticmethod
    def get_env_config() -> Dict[str, Any]:
        """
        Get configuration from environment variables

        Returns:
            Dict[str, Any]: Configuration from environment
        """
        config = {}

        # LLM Configuration
        if 'OPENAI_API_KEY' in os.environ:
            config['api_key'] = os.environ['OPENAI_API_KEY']
        if 'OPENAI_BASE_URL' in os.environ:
            config['base_url'] = os.environ['OPENAI_BASE_URL']

        # Agent Configuration
        if 'AGENT_MODEL_NAME' in os.environ:
            config['model_name'] = os.environ['AGENT_MODEL_NAME']
        if 'AGENT_MAX_TOKENS' in os.environ:
            config['max_tokens'] = int(os.environ['AGENT_MAX_TOKENS'])
        if 'AGENT_TEMPERATURE' in os.environ:
            config['temperature'] = float(os.environ['AGENT_TEMPERATURE'])

        return config