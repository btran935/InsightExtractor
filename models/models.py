import json
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel

class Theme(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thesis_text: str
    embedding: Optional[str] = Field(default=None, alias="_embedding")

    @property
    def _embedding(self) -> List[float]:
        return json.loads(self.embedding) if self.embedding else []

    @_embedding.setter
    def _embedding(self, value: List[float]):
        self.embedding = json.dumps(value)

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    theme_id: int = Field(foreign_key="theme.id")
    post_title: str
    post_url: str = Field(index=True, unique=True)
    published_at: datetime
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    thesis_text: str
