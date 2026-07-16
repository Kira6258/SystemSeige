import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.rate_limit import AUTH_LIMIT, limiter
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.db.session import get_db
from app.models.models import FinancialProfile, User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest

logger = logging.getLogger("clearfinance")
router = APIRouter(prefix="/api/auth", tags=["auth"])

GENERIC_AUTH_ERROR = "Invalid email or password"


def _set_auth_cookies(response: Response, user_id) -> None:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    cookie_kwargs = dict(
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
    )
    response.set_cookie("access_token", access_token, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, **cookie_kwargs)
    response.set_cookie("refresh_token", refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, **cookie_kwargs)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_LIMIT)
async def register(request: Request, body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = User(
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        preferred_language=body.preferred_language,
    )
    db.add(user)
    try:
        await db.flush()
        db.add(FinancialProfile(user_id=user.id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # Generic message — don't confirm whether the email already exists.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")
    except Exception:
        await db.rollback()
        logger.exception("[ERROR] registration failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    _set_auth_cookies(response, user.id)
    return AuthResponse(id=str(user.id), email=user.email, preferred_language=user.preferred_language)


@router.post("/login", response_model=AuthResponse)
@limiter.limit(AUTH_LIMIT)
async def login(request: Request, body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == body.email.lower()))
        user = result.scalar_one_or_none()
        if not user or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=GENERIC_AUTH_ERROR)
    except HTTPException:
        raise
    except Exception:
        logger.exception("[ERROR] login failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    _set_auth_cookies(response, user.id)
    return AuthResponse(id=str(user.id), email=user.email, preferred_language=user.preferred_language)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


@router.get("/me", response_model=AuthResponse)
async def me(user: User = Depends(get_current_user)):
    return AuthResponse(id=str(user.id), email=user.email, preferred_language=user.preferred_language)


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit(AUTH_LIMIT)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    import jwt as pyjwt

    from app.core.security import decode_token

    refresh_token = request.cookies.get("refresh_token")
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not refresh_token:
        raise unauthorized
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except pyjwt.PyJWTError:
        raise unauthorized

    result = await db.execute(select(User).where(User.id == payload.get("sub")))
    user = result.scalar_one_or_none()
    if not user:
        raise unauthorized

    _set_auth_cookies(response, user.id)
    return AuthResponse(id=str(user.id), email=user.email, preferred_language=user.preferred_language)
