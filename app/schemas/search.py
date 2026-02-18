from pydantic import BaseModel, Field


class SearchForm(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)


class SearchResultItem(BaseModel):
    name: str
    category: str
    description: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
