import json
from typing import Dict, Any, Optional
from pathlib import Path
import random
from .exceptions import ConfigError

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to load JSON file {file_path}: {str(e)}")

def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise ConfigError(f"Failed to save JSON file {file_path}: {str(e)}")

def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slashes and ensuring proper format."""
    return url.rstrip('/')

def rotate_user_agent(user_agents: list) -> Optional[str]:
    """Randomly select a user agent from the provided list."""
    return random.choice(user_agents) if user_agents else None

def export_session_state(session_data: Dict[str, Any], file_path: str) -> None:
    """Export session state to a file."""
    save_json_file(session_data, file_path)

def import_session_state(file_path: str) -> Dict[str, Any]:
    """Import session state from a file."""
    return load_json_file(file_path)
