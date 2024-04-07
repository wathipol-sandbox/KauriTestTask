from random import randint
from loguru import logger
from typing import Optional, Union, List, ClassVar
from currencyexplorer.core.exchangers_scraping import (
    AbstractExchangerScraper, ScraperStorageBackendPairData)



class BinanceExchangerCurrencyScraper(AbstractExchangerScraper, EXCHANGER_UNIQ_NAME="binance"):

    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        #logger.info("BINANCE LOADER WORK!!!")
        data1 = ScraperStorageBackendPairData(
            currency_pair_title="USDT_TRC",
            exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME, currency_rate=float(f"0.{randint(1, 8)}"))
        data2 = ScraperStorageBackendPairData(
            currency_pair_title="USDT_BTC",
            exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME, currency_rate=float(f"0.{randint(1, 8)}"))
        return [data1, data2]