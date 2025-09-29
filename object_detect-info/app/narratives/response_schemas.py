# app/narratives/response_schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ObjectDetail(BaseModel):
    name: str
    description: str
    usage: Optional[str]
    benefits: Optional[str]
    origin: Optional[str]
    summary: Optional[str]
    question: str

class DetectionResponse(BaseModel):
    objects: List[ObjectDetail]
    question: str
