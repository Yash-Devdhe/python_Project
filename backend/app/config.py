import os
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

settings = Settings()
