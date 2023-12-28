from typing import Any

from .base_storage import BaseStorage



class State:
    """For working with states."""

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key."""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Get the state by a specific key."""
        state = self.storage.retrieve_state()
        return state.get(key)
