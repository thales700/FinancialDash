from Services.Quotations import Quotations
from Entities.Symbols import Symbols
from Entities.Granularity import Granularity
import logging

logger = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)

print(Quotations().Get(Symbols.AAPL.value, "2023-01-01", "2025-01-31",granularity=Granularity.ONE_MONTH))