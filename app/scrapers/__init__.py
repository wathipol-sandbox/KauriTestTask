from enum import Enum
from currencyexplorer.core.exchangers_scraping import AbstractExchangerScraper
from typing import Dict


#############################################
# All modules containing child classes for AbstractExchangerScraper must be imported here.  #
#   After that new parser will immediately available in the system  #

from .binance import BinanceExchangerCurrencyScraper
from .kraken import KrakenExchangerCurrencyScraper

#############################################


EXCHANGERS_MAPPING: Dict[str, AbstractExchangerScraper] = {
    scraper.EXCHANGER_UNIQ_NAME:
        scraper for scraper in AbstractExchangerScraper.__subclasses__() if hasattr(
                scraper, "EXCHANGER_UNIQ_NAME")
}
EXCHANGERS_MAPPING_ENUM: Enum = Enum(
    'ExchangersMappingEnum', EXCHANGERS_MAPPING.copy())
