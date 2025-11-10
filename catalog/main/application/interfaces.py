from typing import Generic, Optional, Protocol, TypeVar
from uuid import UUID

from django.http import HttpRequest, HttpResponse

GuestSessionID = TypeVar("GuestSessionID", covariant=True)
GuestSessionData = TypeVar("GuestSessionData")
SessionID = TypeVar("SessionID", contravariant=True)
SessionModel = TypeVar("SessionModel")


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


class ICookieBackend(Protocol):
    """Interface for managing cookies: guest and authorized sessions."""

    def set_cookie(
        self,
        response: HttpResponse,
        key: str,
        value: str,
        max_age: int = 86400
    ) -> None:
        """Sets or updates cookies."""
        ...

    def get_cookie(self, request: HttpRequest, key: str) -> str | None:
        """Gets the cookie value."""
        ...

    def delete_cookie(self, response: HttpResponse, key: str) -> None:
        """Clears the cookie by setting it to an empty value."""
        ...


class UUIDGenerator(Protocol):
    """Protocol for callable UUID generators."""

    def __call__(self) -> UUID:
        """Generates a new UUID."""
        ...


class IGuestSessionBackend(Protocol, Generic[GuestSessionID, GuestSessionData]):
    """Abstract interface for managing guest sessions (Django version)."""

    def create_guest_session(self, response: HttpResponse) -> GuestSessionID:
        """Creates a new guest session and stores it in a cookie."""
        ...

    def get_guest_session(self, request: HttpRequest) -> Optional[GuestSessionID]:
        """Gets the current guest session from the cookie."""
        ...

    def delete_guest_session(self, response: HttpResponse) -> None:
        """Deletes a guest session (clears cookies)."""
        ...

    def update_guest_data(
        self,
        request: HttpRequest,
        response: HttpResponse,
        new_data: GuestSessionData,
    ) -> None:
        """Updates guest data while preserving existing data."""
        ...

    def get_guest_data(self, request: HttpRequest) -> GuestSessionData:
        """Gets guest session data from cookies."""
        ...


class ISessionBackend(Protocol, Generic[SessionID, SessionModel]):
    """
    Abstract interface that defines methods 
    for interacting with session data (sync version).
    """

    def create(self, session_id: SessionID, data: SessionModel) -> None:
        """Create a new session."""
        ...

    def read(self, session_id: SessionID) -> Optional[SessionModel]:
        """Read session data from the storage."""
        ...

    def update(self, session_id: SessionID, data: SessionModel) -> None:
        """Update session data in the storage."""
        ...

    def delete(self, session_id: SessionID) -> None:
        """Remove session data from the storage."""
        ...
