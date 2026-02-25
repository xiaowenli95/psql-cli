"""Configuration management for the application."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration."""
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database: str = os.getenv("POSTGRES_DB", "testdb")
    user: str = os.getenv("POSTGRES_USER", "readonly_user")
    password: str = os.getenv("POSTGRES_PASSWORD", "readonly_pass")

    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class OllamaConfig:
    """Ollama configuration."""
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "mistral")
    timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))


@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig
    ollama: OllamaConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            database=DatabaseConfig(),
            ollama=OllamaConfig()
        )
