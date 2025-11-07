import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from entities.Distribution import DistributionType
from schemas.symbol_properties import SymbolProperties
from services.GarchLevels import GarchLevels
from entities.Granularity import Granularity
from entities.ArchModels import ArchModelType
from entities.Symbols import Symbols
import pandas as pd
import logging

logger = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)

symbolInfos = SymbolProperties(
    symbol=Symbols.AAPL,
    start_date="2025-10-01",
    end_date="2025-10-31",
    granularity=Granularity.FIFTEEN_MINUTES
)

modelType = ArchModelType.GARCH

df = GarchLevels().GetLevels(symbolInfos, modelType, distribution=DistributionType.NORMAL, levels=3)
print(df)