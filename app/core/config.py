from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"

settings = Settings()        
