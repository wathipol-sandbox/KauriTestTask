from random import randint
from loguru import logger
from typing import Optional, Union, List
from currencyexplorer.core.exchangers_scraping import (
    AbstractExchangerScraper, ScraperStorageBackendPairData)


class KrakenExchangerCurrencyScraper(AbstractExchangerScraper, EXCHANGER_UNIQ_NAME="kraken"):

    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        #logger.info("KRAKEN LOADER WORK!!!")
        data1 = ScraperStorageBackendPairData(
            currency_pair_title="USDT_ETH",
            exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME, currency_rate=float(f"0.{randint(1, 25)}"))
        data2 = ScraperStorageBackendPairData(
            currency_pair_title="USDT_BTC",
            exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME, currency_rate=float(f"0.{randint(1, 16)}"))
        return [data1, data2]