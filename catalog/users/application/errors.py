class ServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthError(ServiceError):
    def __init__(
        self, 
        message: str = "Ошибка авторизации", 
        status_code: int = 401
    ) -> None:
        super().__init__(message, status_code)


class BlockedError(ServiceError):
    def __init__(self, message: str = "Аккаунт временно заблокирован") -> None:
        super().__init__(message, status_code=403)


class PermissionDenied(ServiceError):
    def __init__(self, message: str = "Недостаточно прав") -> None:
        super().__init__(message, status_code=403)


class NotFoundError(ServiceError):
    def __init__(self, message: str = "Объект не найден") -> None:
        super().__init__(message, status_code=404)


class ConflictError(ServiceError):
    """Ошибка конфликта (например, ресурс уже существует)."""
    def __init__(self, message: str = "Ресурс уже существует") -> None:
        super().__init__(message, status_code=409)


class InternalError(ServiceError):
    """Внутренняя ошибка сервиса (любая непредвиденная ошибка)."""
    def __init__(self, message: str = "Внутренняя ошибка сервиса") -> None:
        super().__init__(message, status_code=500)