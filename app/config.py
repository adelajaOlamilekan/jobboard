from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str
    SMTP_HOST: str = None
    SMTP_PORT: int = 465
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    EMAIL_FROM: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    # FRONTEND_BASE_URL: AnyHttpUrl = "http://localhost:3000"
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    class Config:
        env_file = ".env"

settings = Settings()
