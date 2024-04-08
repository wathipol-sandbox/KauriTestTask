import time
import traceback
from httpx import AsyncClient
from random import randint
from loguru import logger
from typing import Optional, Union, List, Dict
from currencyexplorer.core.exchangers_scraping import (
    AbstractExchangerScraper, ScraperStorageBackendPairData)


class KrakenExchangerCurrencyScraper(
        AbstractExchangerScraper,
        EXCHANGER_UNIQ_NAME="kraken",
        DEFAULT_LISTNER_TIMEOUT=30, LISTNER_AUTO_START=False):
    
    TICKER_URL: str = "https://api.kraken.com/0/public/Ticker"

    async def _get_ticker_data(self, pair: str | None =  None):
        """ GET ticker data object from Kraken API """
        response_data = {}
        params = {}
        if pair is not None:
            params["pair"] = pair
        try:
            async with AsyncClient() as client:
                response = await client.get(self.TICKER_URL, params=params)
                response_data = response.json()
        except Exception as e:
            logger.info(traceback.format_exc())
        else:
            response_data = response_data.get("result", {})
        return response_data

    def _scraper_data_list_from_response(
            self, kraken_ticker_data: Dict[str, dict],
            swap_price: bool | None = False,
            pair: str | None = None) -> List[ScraperStorageBackendPairData]:
        """
            make list of scraper pair data objects from kraken ticker response
        """
        if kraken_ticker_data is None:
            return []
        data_list = []
        for k_pair, k_item in kraken_ticker_data.items():
            ask_price, bid_price, close_price = list(map(lambda x: x[0], list(k_item.values())[:3]))
            symbol = None if pair is None else str(pair)
            if symbol is None:
                symbol = f"{k_pair[0:3]}_{k_pair[4:]}" if swap_price is False else f"{k_pair[4:]}_{k_pair[0:3]}"
            avr_price = (float(ask_price) + float(bid_price)) / 2
            new_data = ScraperStorageBackendPairData(
                exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME,
                currency_pair_title=symbol,
                currency_rate=avr_price if (not swap_price or avr_price == 0) else 1 / avr_price,
                last_update=time.time()
            )
            data_list.append(new_data)
        return data_list

    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        
        # load only for specified pair
        if pair_title is not None:
            symbol_pair = str(pair_title).split("_")
            kraken_pair_data = await self._get_ticker_data(pair=f"{symbol_pair[0]}{symbol_pair[1]}")
            swap_price = False
            if len(kraken_pair_data) == 0:
                kraken_pair_data = await self._get_ticker_data(
                    pair=f"{symbol_pair[1]}{symbol_pair[0]}")
                swap_price = True
            return self._scraper_data_list_from_response(
                kraken_pair_data, swap_price=swap_price, pair=pair_title)
        
        # Load for all aviable pairs
        return self._scraper_data_list_from_response(await self._get_ticker_data())
