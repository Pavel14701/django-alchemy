from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError
from config import SecretConfig

from users.application.interfaces import PasswordHasherProtocol


class Argon2PasswordHasher(PasswordHasherProtocol):
    def __init__(
        self, 
        config: SecretConfig
    ) -> None:
        self._hasher = Argon2Hasher()
        self._pepper = config.pepper

    def hash(self, password: str, salt: str | None = None) -> str:
        salted_password = f"{password}{salt or ''}{self._pepper}"
        return self._hasher.hash(salted_password)

    def verify(self, hashed: str, password: str, salt: str | None = None) -> bool:
        try:
            return self._hasher.verify(hashed, f"{password}{salt or ''}{self._pepper}")
        except VerifyMismatchError:
            return False
