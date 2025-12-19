from pydantic import BaseModel
from typing import Optional

class Date(BaseModel):
    date: str

class PersonsByPortfolioRquest(BaseModel):
    activeDate: Date
    president_id: str