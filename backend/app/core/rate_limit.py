from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)

AUTH_LIMIT = "5/minute"
AI_LIMIT = "3/minute"
GENERAL_LIMIT = "100/minute"
