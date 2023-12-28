import abc
from typing import Any


class BaseStorage(abc.ABC):
    """Abstract state storage.

    Allows you to save and receive the state.
    The way the state is stored may vary depending on
    from the final implementation. For example, you can store information
    in a database or in a distributed file storage.
    """

    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        """Save state to the storage."""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        """Get the state from the storage."""
        pass
