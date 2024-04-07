import time
import json
from loguru import logger
from typing import Optional, Union, List, ClassVar
from currencyexplorer import binance_async_client
from currencyexplorer.core.exchangers_scraping import (
    AbstractExchangerScraper, ScraperStorageBackendPairData)


class BinanceExchangerCurrencyScraper(
    AbstractExchangerScraper,
    EXCHANGER_UNIQ_NAME="binance", DEFAULT_LISTNER_TIMEOUT=30, LISTNER_AUTO_START=False):

    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        kwargs = {}
        swap_price = False
        if pair_title is not None:
            pair_list = str(pair_title).split("_")
            kwargs["symbol"] = "".join(
                (pair_list[1], pair_list[0],) if pair_list[0] == "USDT" else pair_list)
            swap_price = pair_list[0] == "USDT"
        ticker_data = await binance_async_client.get_ticker(**kwargs)
        if not isinstance(ticker_data, (tuple, list, )):
            ticker_data = [ticker_data]
        data_list = []
        for ticker in ticker_data:
            symbol = str(ticker["symbol"])
            if pair_title is not None:
                symbol= str(pair_title)
            else:
                symbol = f"{symbol[0:3]}_{symbol[4:]}"
            ask_price = ticker["askPrice"]
            bid_price = ticker["bidPrice"]
            avr_price = (float(ask_price) + float(bid_price)) / 2
            new_data = ScraperStorageBackendPairData(
                exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME,
                currency_pair_title=symbol,
                currency_rate=avr_price if not swap_price else 1 / avr_price,
                last_update=time.time()
            )
            data_list.append(new_data)
        return data_list
