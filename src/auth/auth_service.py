import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException
from datetime import datetime, timedelta


JWT_SECRET = "your_jwt_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60


class AuthService:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    def create_token(self, email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_token_from_cookie(self, request: Request) -> str:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return token


auth_service = AuthService()
