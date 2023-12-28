import json
from json import JSONDecodeError
from logging import Logger
from typing import Any

from .base_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    """Implementation of a storage using a local file.

    Storage format: JSON
    """

    def __init__(self, logger: Logger, file_path: str | None = 'state.json') -> None:
        self.file_path = file_path
        self._logger = logger

    def save_state(self, state: dict[str, Any]) -> None:
        """Save state to storage."""
        with open(self.file_path, 'w') as file:
            json.dump(state, file)

    def retrieve_state(self) -> dict[str, Any]:
        """Get state from storage."""
        try:
            with open(self.file_path, 'r') as file:
                state = json.load(file)
                self._logger.info(f"State '{state}'")
                return state
        except (FileNotFoundError, JSONDecodeError):
            self._logger.warning(
                'No state file provided')
            return {}
