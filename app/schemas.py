from typing import List, Optional
from pydantic import BaseModel

class UploadResponse(BaseModel):
    result: dict
