import os
from pathlib import Path

from dotenv import dotenv_values


def read_dotenv(root: str) -> None:
    """Read a .env file in the given root path."""
    env_path = Path(root) / ".env"
    if env_path.exists():
        env_config = dotenv_values(f"{env_path}")
        for key, value in env_config.items():
            # if key not in os.environ:  # 为了安全？
            os.environ[key] = value or ""
