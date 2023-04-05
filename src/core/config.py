import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING


class AppSettings(BaseSettings):
    app_title: str = 'LibraryApp'
    database_dsn: PostgresDsn
    project_name: str
    project_host: str
    project_port: int
    secret_key: str
    token_expire_minutes: int
    algorithm: str
    redis_url: str
    redis_host: str = 'cache'
    redis_port: int = 6379

    class Config:
        env_file = '.env'


app_settings = AppSettings()
logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
