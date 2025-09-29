from pydantic_settings import BaseSettings
import torch
import os

class Settings(BaseSettings):
    model_path: str = "data/artifacts/yolov8n.pt"
    debug: bool = True
    huggingfacehub_api_token: str | None = None  # optional

    @property
    def device(self):
        return "cuda" if torch.cuda.is_available() else "cpu"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Only set env variable if token exists
if settings.huggingfacehub_api_token:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.huggingfacehub_api_token
