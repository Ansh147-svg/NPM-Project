"""Authentication and RBAC dependencies for FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate JWT and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.get(User, token_data.sub)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def require_roles(*roles: str):
    """Factory returning a dependency that enforces role-based access."""
    async def role_checker(user: User = Depends(get_current_user)):
        user_role_names = {r.name for r in user.roles}
        if user.is_superuser:
            return user
        if not user_role_names.intersection(roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker


require_admin = require_roles("admin", "superuser")