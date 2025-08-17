from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    react_app_vapi_api_key: str
    react_app_vapi_assistant_id: str

    class Config:
        env_file = ".env"

settings = Settings()