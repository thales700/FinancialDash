import datetime
import yfinance as yf
import pandas as pd
from entities.Symbols import Symbols
from entities.Granularity import Granularity
from typing import Union, Optional
import logging
from schemas.symbol_properties import SymbolProperties

logger = logging.getLogger(__name__)

class Quotations:
    def __init__(self) -> None:
        self.symbolsValues = [key for key in Symbols.__members__.keys()]
    
    def _VerifySymbol(self, symbol: str) -> bool:
        return symbol in self.symbolsValues

    def _VerifyDate(self, date: str) -> bool:
        try:
            datetime.date.fromisoformat(date)
            return True
        except ValueError:
            logger.error(f"Date format error: {date} is not in YYYY-MM-DD format.")
            return False
        
    def Get(self, symbol: SymbolProperties) -> Union[pd.DataFrame, str]:
        try:
            if not self._VerifySymbol(symbol.symbol.value):
                return "No such symbol"
            
            if not self._VerifyDate(symbol.start_date) or not self._VerifyDate(symbol.end_date):
                return "Date format error. Use YYYY-MM-DD."

            else:
                ticker = yf.Ticker(symbol.symbol.value)
                data = ticker.history(start=symbol.start_date, end=symbol.end_date, interval=symbol.granularity.value)
                df = pd.DataFrame(data)
                logger.info(f"Successfully retrieved data for {symbol} from {symbol.start_date} to {symbol.end_date}")
                return df
            
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol} from {symbol.start_date} to {symbol.end_date}: {e}")
            return str(e)