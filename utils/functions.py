import sys
from pathlib import Path

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DIR : str = str(Path(__file__).resolve().parent.parent) + '/'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sys.path.append(self.BASE_DIR)

settings = Settings()