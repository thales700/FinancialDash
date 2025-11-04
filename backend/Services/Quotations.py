import datetime
import yfinance as yf
import pandas as pd
from Entities.Symbols import Symbols
from Entities.Granularity import Granularity
from typing import Union, Optional
import logging

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
        
    def Get(self, symbol: str, start_date: str, end_date: str, granularity: Granularity) -> Union[pd.DataFrame, str]:
        try:
            if not self._VerifySymbol(symbol):
                return "No such symbol"
            
            if not self._VerifyDate(start_date) or not self._VerifyDate(end_date):
                return "Date format error. Use YYYY-MM-DD."

            else:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, interval=granularity)
                df = pd.DataFrame(data)
                logger.info(f"Successfully retrieved data for {symbol} from {start_date} to {end_date}")
                return df
            
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol} from {start_date} to {end_date}: {e}")
            return str(e)