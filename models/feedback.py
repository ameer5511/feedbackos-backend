from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class FeedbackItem(BaseModel):
    id: UUID = None
    workspace_id: UUID
    raw_text: str
    source: str              # 'paste' | 'csv' | 'webhook'
    source_meta: dict = {}
    char_count: int = 0
    is_embedded: bool = False
    ingested_at: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.id or uuid4()
        self.char_count = len(self.raw_text)
        self.ingested_at = self.ingested_at or datetime.utcnow()
        

        