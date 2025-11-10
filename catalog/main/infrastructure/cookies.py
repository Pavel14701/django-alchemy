from django.http import HttpRequest, HttpResponse

from main.application.interfaces import ICookieBackend


class CookieRepo(ICookieBackend):
    """Class for managing cookies: guest and authenticated sessions (Django version)."""

    GUEST_COOKIE = "guest_session"
    AUTH_COOKIE = "auth_session"
    DATA_COOKIE = "guest_data"

    def set_cookie(
        self,
        response: HttpResponse,
        key: str,
        value: str,
        max_age: int = 86400
    ) -> None:
        """Sets or updates a cookie."""
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            max_age=max_age,
            secure=True,
            samesite="Strict"
        )

    def get_cookie(self, request: HttpRequest, key: str) -> str | None:
        """Retrieves the value of a cookie."""
        return request.COOKIES.get(key)

    def delete_cookie(self, response: HttpResponse, key: str) -> None:
        """Deletes a cookie."""
        response.delete_cookie(
            key=key,
            path="/",
            samesite="Strict"
        )
