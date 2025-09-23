from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost/dbname")

    # Firebase
    firebase_credentials_path: str = Field(default="firebase-credentials.json")

    # JWT
    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Judge0 API
    judge0_api_url: str = Field(default="https://api.judge0.com")

    # Twilio
    twilio_account_sid: str = Field(default="")
    twilio_auth_token: str = Field(default="")
    twilio_phone_number: str = Field(default="")

    # SendGrid
    sendgrid_api_key: str = Field(default="")

    # Blockchain API
    blockchain_api_url: str = Field(default="https://api.blockchain.com")
    blockchain_api_key: str = Field(default="")

    # AI Models
    ai_model_path: str = Field(default="models/")

    class Config:
        env_file = ".env"

settings = Settings()
