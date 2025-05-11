import re
from pydantic import BaseModel, validator
from typing import List, Optional

class Article(BaseModel):
    id: Optional[str] = None
    title: str
    authors: list
    abstract: str

    """
    @validator('id')
    def validate_arxiv_id(cls, v):
        if not re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', v):
            raise ValueError('Invalid arXiv ID format')
        return v """

    class Config:
        schema_extra = {
            "example": {
                "title": "Example title",
                "authors": "Author1. Author2",
                "abstract": "Example abstract text"
            }
        }

class Articles(BaseModel):
    articles: List[Article]

    class Config:
        schema_extra = {
            "example:":{
                "articles":[
                    {
                        "title": "Example title 1",
                        "authors": "Author1. Author2",
                        "abstract": "Example abstract 1"
                    },
                    {
                        "title": "Example title 2",
                        "authors": "Author1. Author2",
                        "abstract": "Example abstract 2"
                    }
                ]
            }
        }