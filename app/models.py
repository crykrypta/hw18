from typing import List
from pydantic import BaseModel


class Query(BaseModel):
    topic: str
    username: str
    dialog: List[str]
