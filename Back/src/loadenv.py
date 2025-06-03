from pydantic import BaseSettings

class Config(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    DATABASEB_URI: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int