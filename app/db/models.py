from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CatalogItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=120)
    category: str = Field(index=True, max_length=80)
    description: str = Field(max_length=400)


class SearchLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
