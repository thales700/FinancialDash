import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from entities.Granularity import Granularity
from services.Quotations import Quotations
from schemas.symbol_properties import SymbolProperties
from entities.Symbols import Symbols
#from entities.Granularity import Granularity
import pandas as pd
import logging

logger = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)

symbol = SymbolProperties(
    symbol=Symbols.AAPL,
    start_date="2025-01-01",
    end_date="2025-01-31",
    granularity=Granularity.ONE_DAY
)

df = Quotations().Get(symbol)
print(df)