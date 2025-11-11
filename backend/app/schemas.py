from pydantic import BaseModel
from typing import Any, Dict

class ResumeIn(BaseModel):
    template_id: int
    data: Dict[str, Any]

class SuggestIn(BaseModel):
    data: Dict[str, Any]
    template_id: int
from pydantic import BaseModel
from typing import Any, Dict, Optional

class SuggestIn(BaseModel):
    data: Dict[str, Any]
    template_id: int
    mode: Optional[str] = None  # 👈 Added
