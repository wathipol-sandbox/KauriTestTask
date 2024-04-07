import asyncio
from typing import Optional, Union, List, ClassVar, Any, AsyncIterator
from .storage_backends import (ScraperStorageBackendPairData)
from abc import ABC, abstractmethod


class AbstractExchangerScraper(ABC):
    """Abstract class specification for cryptocurrency rate data scraper from some exchanges platform.
            Classes that implement the logic for scraping data from specified exchange
                must be a child from this class.
            IF EXCHANGER_UNIQ_NAME attr not defined on child class scraper name
                will be created from class name (Abstract.__init_subclass__ method)
    """

    EXCHANGER_UNIQ_NAME: ClassVar[str]

    def __init__(self) -> None:
        self._worker_stop_signal: Optional[bool] = False
        self._worker_running_status: Optional[bool] = False

    def __init_subclass__(cls, /, *, EXCHANGER_UNIQ_NAME: Optional[str] = None, **kwargs: Any) -> None:
        if hasattr(cls, "EXCHANGER_UNIQ_NAME") is False and EXCHANGER_UNIQ_NAME is None:
            # Generate exchaner scraper uniq_name from scraper class name if EXCHANGER_UNIQ_NAME not defined
            new_uniq_name = str(cls.__name__).lower()
            for skip_word in ('scraper', 'currency', 'exchanger'):
                new_uniq_name = new_uniq_name.replace(skip_word, '')
            cls.EXCHANGER_UNIQ_NAME = new_uniq_name
        else:
            cls.EXCHANGER_UNIQ_NAME = str(EXCHANGER_UNIQ_NAME)
        return super().__init_subclass__(**kwargs)

    @abstractmethod
    async def get_currency(
            self, pair_title: Optional[str] = None) -> Union[
                List[ScraperStorageBackendPairData], ScraperStorageBackendPairData]:
        """
            This method should implement logic for currency rate data fetching.
                IF pair_title is None should return all aviable pairs for specified exchager.
            
            - CURRENCY RATE MUST BE average value between buy/sell currency rate price!!!

        """
        raise NotImplementedError
    
    @property
    def currency_listener_status(self) -> bool:
        """This property method should implement logic for check currency listener process status.
            By default, this method implement checking status logic for listener loop.
                SHOULD be overridden if currency listener logic changed.
        """
        return self._worker_running_status
    
    async def attach_currency_listener(
            self, *args,
            delay_seconds: Optional[float] = 0.1, max_update_iteration: Optional[int] = None,
            **kwargs) -> AsyncIterator[List[ScraperStorageBackendPairData] | ScraperStorageBackendPairData]:
        """This method is an asynchronous generator that can be used to actively obtain exchange rates.
                By default, it uses the get_currency() logic for receiving exchange rates, can be overridden
                    if active receiving can be more effective for specified exchanger.
                        (For example, supporting an open web socket with Binance)
        """
        current_iteration_count = 0
        self._worker_running_status = True
        while not self._worker_stop_signal:
            if isinstance(max_update_iteration, int) and max_update_iteration is not None:
                current_iteration_count += 1
            await asyncio.sleep(delay_seconds)
            data = await self.get_currency(*args, **kwargs)
            yield data
            if isinstance(max_update_iteration, int) and current_iteration_count >= max_update_iteration:
                break
        self._worker_running_status = False
    
    async def stop_currency_listener(self) -> None:
        """This method implement logic for stop currency listener process.
            By default, this method set bool flag for break currency listener loop
                in default implementation. SHOULD be overridden if currency listener logic changed.
        """
        self._worker_stop_signal = True
