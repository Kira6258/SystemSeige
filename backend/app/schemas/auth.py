import re

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import StrictModel

_PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")


class RegisterRequest(StrictModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    preferred_language: str = Field(default="en", max_length=10)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, and one digit")
        return v


class LoginRequest(StrictModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(StrictModel):
    id: str
    email: str
    preferred_language: str
