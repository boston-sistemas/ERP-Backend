from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashService:
    @staticmethod
    def hash_text(plain_text: str) -> str:
        return pwd_context.hash(plain_text, rounds=12)

    @staticmethod
    def verify_text(plain_text: str, hashed_text: str) -> bool:
        return pwd_context.verify(plain_text, hashed_text)
