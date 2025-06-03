from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URI: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file='.env'