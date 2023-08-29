from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    apiKey: str
    authDomain: str
    databaseURL: str
    projectId: str
    storageBucket: str
    messagingSenderId: str
    appId: str
    measurementId: str
    wep_api_key: str

    class Config:
        env_file = "./.env"


settings = Settings()
