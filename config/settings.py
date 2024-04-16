import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_DIR : str = str(Path(__file__).resolve().parent.parent) + '/'
    PROJECT_DIR: str = BASE_DIR + 'mecsa_erp/'
    ENV_FILE : str = BASE_DIR + '.env'   
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_ignore_empty=True, extra="ignore")
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MECSA ERP - API"
    DATABASE_URL : str
    
    sys.path.append(BASE_DIR)

settings = Settings()

if __name__ == "__main__":
    print(settings.model_dump())