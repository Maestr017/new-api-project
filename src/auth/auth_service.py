import jwt
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from src.core.config import settings


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60


class AuthService:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    @staticmethod
    def create_token(user_email: str) -> str:
        payload = {
            "sub": user_email,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_token_from_cookie(request: Request) -> str:
        token = request.cookies.get("access_token")
        return token

    @staticmethod
    def hash_password(password: str) -> str:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


auth_service = AuthService()
