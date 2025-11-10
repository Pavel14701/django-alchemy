from typing import Protocol


class ISession(Protocol):
    """Interface for session transaction management."""

    def commit(self) -> None:
        """Commits changes in the session."""
        ...

    def flush(self) -> None:
        """Flushes changes without committing the transaction."""
        ...

    def rollback(self) -> None:
        """Rolls back changes in the session."""
        ...
