from pydantic import BaseModel
from entities.Granularity import Granularity
from entities.Symbols import Symbols

class SymbolProperties(BaseModel):
    symbol: Symbols
    start_date: str
    end_date: str
    granularity: Granularity