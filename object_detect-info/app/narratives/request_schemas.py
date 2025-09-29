from pydantic import BaseModel

class ImageUploadRequest(BaseModel):
    filename: str