import asyncio
import time
import json
from loguru import logger
from typing import Optional, Union, List, ClassVar, AsyncIterator, Dict
from binance import BinanceSocketManager
from currencyexplorer import binance_async_client
from currencyexplorer.core.exchangers_scraping import (
    AbstractExchangerScraper, ScraperStorageBackendPairData)


class BinanceExchangerCurrencyScraper(
    AbstractExchangerScraper,
    EXCHANGER_UNIQ_NAME="binance", DEFAULT_LISTNER_TIMEOUT=1, LISTNER_AUTO_START=True):

    async def _ticker_response_to_data_list(
            self,
            ticker_data: dict,
            swap_price: Optional[bool] = False,
            pair_title: Optional[str] = None,
            use_binance_average_price: Optional[bool] = False,
            message_title_mapping: Optional[Dict[str, str]] = {}
            ) -> List[ScraperStorageBackendPairData]:
        """
            util for make list of scraper data objects from binance response
        """
        if not isinstance(ticker_data, (tuple, list, )):
            ticker_data = [ticker_data]
        data_list = []
        for ticker in ticker_data:
            symbol = str(ticker[message_title_mapping.get("symbol", "symbol")])
            if pair_title is not None:
                symbol= str(pair_title)
            else:
                symbol = f"{symbol[0:3]}_{symbol[4:]}"
            avr_price = None
            if use_binance_average_price is not True:
                ask_price = ticker[message_title_mapping.get("askPrice", "askPrice")]
                bid_price = ticker[message_title_mapping.get("askPrice", "askPrice")]
                avr_price = (float(ask_price) + float(bid_price)) / 2
            else:
                avr_price = ticker[message_title_mapping.get("WeightedAvgPrice", "WeightedAvgPrice")]
            new_data = ScraperStorageBackendPairData(
                exchanger_uniq_name=self.EXCHANGER_UNIQ_NAME,
                currency_pair_title=symbol,
                currency_rate=avr_price if not swap_price else 1 / avr_price,
                last_update=time.time()
            )
            data_list.append(new_data)
        return data_list

    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        kwargs = {}
        swap_price = False
        if pair_title is not None:
            pair_list = str(pair_title).split("_")
            kwargs["s"] = "".join(
                (pair_list[1], pair_list[0],) if pair_list[0] == "USDT" else pair_list)
            swap_price = pair_list[0] == "USDT"
        ticker_data = await binance_async_client.get_ticker(**kwargs)
        return await self._ticker_response_to_data_list(
            ticker_data, swap_price=swap_price, pair_title=pair_title)

    async def attach_currency_listener(
            self, *args,
            delay_seconds: Optional[float] = None, max_update_iteration: Optional[int] = None,
            **kwargs) -> AsyncIterator[List[ScraperStorageBackendPairData] | ScraperStorageBackendPairData]:
        current_iteration_count = 0
        self._worker_running_status = True
        bm = BinanceSocketManager(binance_async_client)
        ts = bm.ticker_socket()

        async with ts as tscm:
            while not self._worker_stop_signal:
                if isinstance(max_update_iteration, int) and max_update_iteration is not None:
                    current_iteration_count += 1
                await asyncio.sleep(
                    delay_seconds if delay_seconds is not None else self.DEFAULT_LISTNER_TIMEOUT)
                ticker_data = await tscm.recv()
                data = await self._ticker_response_to_data_list(
                    ticker_data,
                    use_binance_average_price=True,
                    message_title_mapping={
                        "WeightedAvgPrice": "x", "symbol": "s"})
                yield data
                if isinstance(max_update_iteration, int) and current_iteration_count >= max_update_iteration:
                    break
        self._worker_running_status = False
    
    async def stop_currency_listener(self) -> None:
        self._worker_stop_signal = True
