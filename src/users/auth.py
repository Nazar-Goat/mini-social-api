from passlib.context import CryptContext
from src.config import  get_settings
from jose import jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# function to create a password hash
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# function to verify a password against a hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    settings = get_settings()
    
    now= datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, settings.get_auth_data()["secret_key"], algorithm=settings.get_auth_data()["algorithm"])
    
def create_refresh_token(user_id: int) -> str:
    settings = get_settings()
    
    now= datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }

    return jwt.encode(payload, settings.get_auth_data()["secret_key"], algorithm=settings.get_auth_data()["algorithm"])
    
def to_decode(token: str) -> dict:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token, 
            settings.get_auth_data()["secret_key"],
            algorithms=[settings.get_auth_data()["algorithm"]]
        )

        if payload.get("sub") is None:
            return None
        
        return payload
    except jwt.JWTError:
        return None