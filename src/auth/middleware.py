from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from starlette.responses import JSONResponse
from src.auth.auth_service import auth_service
from src.core.logger import logger


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_paths: list[str] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or []

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(ep) for ep in self.exempt_paths):
            return await call_next(request)

        token = auth_service.get_token_from_cookie(request)
        logger.debug(f"Token from cookie: {token}")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        try:
            payload = auth_service.decode_token(token)
            logger.debug(f"Decoded payload: {payload}")
            request.state.user_email = payload.get("sub")
            if not request.state.user_email:
                logger.debug("No token found in cookies")
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.debug(f"Auth middleware error: {e}")
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        response = await call_next(request)
        return response
