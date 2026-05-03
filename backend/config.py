from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "imovia-secret-key-2024")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 horas
    
    # AWS S3
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_bucket_name: str = os.getenv("AWS_BUCKET_NAME", "imovia-images")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"


settings = Settings()