# user_config.py
import json
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class User:
    name: str
    search_query: str
    spreadsheet_id: str
    work_preferences: Optional[Dict] = None


def load_user_config(config_file: str = "config/user.json") -> User:
    """Loads a single user configuration from a JSON file."""
    try:
        with open(config_file, "r") as f:
            user_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{config_file}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in '{config_file}'.")

    return User(
        name=user_data["name"],
        search_query=user_data["search_query"],
        spreadsheet_id=user_data["spreadsheet_id"],
        work_preferences=user_data.get("work_preferences"),
    )
