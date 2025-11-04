from enum import Enum

class Symbols(Enum):
    AAPL = "AAPL"
    MSFT = "MSFT"
    GOOGL = "GOOGL"
    AMZN = "AMZN"
    TSLA = "TSLA"

    def __str__(self):
        return self.value