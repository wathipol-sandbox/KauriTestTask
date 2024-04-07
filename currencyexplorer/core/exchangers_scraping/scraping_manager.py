import asyncio
import time
from loguru import logger
from inspect import isclass
from typing import Optional, Union, List, Dict, Type, AsyncIterator
from .storage_backends import (
    AbstractScraperStorageBackend, CurrencyScraperAsyncSafeDictStorage, ScraperStorageBackendPairData)
from .abstract_exchanger_scraper import AbstractExchangerScraper


class ExchangersScrapingManager:
    """Interface class for managing currency scraper system
            You can implement your own backend for storing data
                and use it to operate currency rate scrapers. (See. AbstractScraperStorageBackend )
    """
    
    def __init__(
            self,
            scrapers_list: List[Type[AbstractExchangerScraper]],
            storage_backend: Optional[
                AbstractScraperStorageBackend] = CurrencyScraperAsyncSafeDictStorage()) -> None:
        self._storage_backend = storage_backend
        self.__scrapers_list = {}
        self.append_to_scrapers(*scrapers_list)
    
    def append_to_scrapers(self, *scrapers: List[Type[AbstractExchangerScraper]]) -> None:
        """ Add new scraper method to manager flow """
        for SCRAPER_TYPE in scrapers:
            if not issubclass(SCRAPER_TYPE, AbstractExchangerScraper):
                raise TypeError("scrappers must be tuple of AbstractExchangerScraper subclasses")
            if SCRAPER_TYPE.EXCHANGER_UNIQ_NAME in self.__scrapers_list:
                raise NameError("{} already exist in scraping manager flow".format(
                    SCRAPER_TYPE.EXCHANGER_UNIQ_NAME))
            self.__scrapers_list[SCRAPER_TYPE.EXCHANGER_UNIQ_NAME] = SCRAPER_TYPE()

    async def rm_from_scrapers(
            self,
            *scrapers: List[
                Union[str, Type[AbstractExchangerScraper], AbstractExchangerScraper]]) -> None:
        """ RM scraper method from manager flow """
        try:
            fixed_to_rm_list = [
                scraper if isinstance(
                    scraper, str) else str(scraper.EXCHANGER_UNIQ_NAME) for scraper in scrapers
            ]
        except AttributeError:
            raise TypeError("scrapers must be tuple of scrapers name or object/instance")

        for to_rm_scraper in fixed_to_rm_list:
            if to_rm_scraper not in self.__scrapers_list:
                raise NameError("{} scraper not found in scraping manager flow".format(to_rm_scraper))
    
    async def get_scraper(
            self, scraper: Union[
                str, Type[AbstractExchangerScraper], AbstractExchangerScraper]) -> AbstractExchangerScraper:
        """ GET scraper instance object from scraping manager flow """
        s_name = scraper
        if (
                isclass(scraper) is True and issubclass(
                    scraper, AbstractExchangerScraper)) or isinstance(scraper, AbstractExchangerScraper):
            s_name = str(scraper.EXCHANGER_UNIQ_NAME)
        if s_name not in self.__scrapers_list:
            raise NameError("{} scraper instance not found in scraping flow".format(s_name))
        return self.__scrapers_list[s_name]
    
    async def get_scrapers(self):
        """ GET list of scraper objects list from scraping manager flow """
        return list(self.__scrapers_list.values())
    
    async def iter_scrapers(self) -> AsyncIterator[AbstractExchangerScraper]:
        """ITER in scraper instance objects from scraping manager flow.
        Return: AsyncGenerator[AbstractExchangerScraper]
        """
        for scraper in list(self.__scrapers_list.values()):
            yield scraper

    async def update_from_scraper(self, scraper: Union[
                str, Type[AbstractExchangerScraper], AbstractExchangerScraper]) -> None:
        """ Update currency data from specified scraper """
        scraper_obj = await self.get_scraper(scraper)
        scraper_response = await scraper_obj.get_currency()
        if isinstance(scraper_response, ScraperStorageBackendPairData):
            scraper_response = [scraper_response]
        elif not isinstance(scraper_response, list):
            raise TypeError(
                "scraper method should return scope of ScraperStorageBackendPairData objects")
        
        for data in scraper_response:
            data.exchanger_uniq_name = str(scraper_obj.EXCHANGER_UNIQ_NAME)
            await self._storage_backend.store_pair_data(data)

    async def update_all(self) -> None:
        """ Update currency data from all scrapers """
        for scraper_uniq_name in self.__scrapers_list:
            await self.update_from_scraper(scraper_uniq_name)
    
    async def _updater_process(self, scraper: AbstractExchangerScraper, *args, **kwargs) -> None:
        """ Scraper manager flow system wrapper method
                Listing updates from scraper and store to backend.
        """
        async for updates in scraper.attach_currency_listener():
            scraper_response = updates
            if isinstance(updates, ScraperStorageBackendPairData):
                scraper_response = [scraper_response]
            elif not isinstance(updates, list):
                raise TypeError(
                    "scraper method should return scope of ScraperStorageBackendPairData objects")
    
            for data in scraper_response:
                data.exchanger_uniq_name = str(scraper.EXCHANGER_UNIQ_NAME)
                await self._storage_backend.store_pair_data(data)
    
    async def run_active_updater(self, *args, **kwargs) -> None:
        """ Run update handler process for all available scrapers """
        for scraper_uniq_name, scraper in self.__scrapers_list.items():
            logger.info("{}: creating task for {} updater...".format(
                self.__class__.__name__, scraper_uniq_name))
            asyncio.create_task(self._updater_process(scraper, *args, **kwargs))
            logger.info("{}: updater task {} ready!".format(
                self.__class__.__name__, scraper_uniq_name))
    
    async def stop_active_updater(self, *args, **kwargs) -> None:
        """ Stop update handler process for all aviable scrapers """
        for scraper_uniq_name, scraper in self.__scrapers_list.items():
            await scraper.stop_currency_listener(*args, **kwargs)

    async def get(
                self,
                scraper: Union[str, Type[AbstractExchangerScraper], AbstractExchangerScraper],
                pair_title: Optional[str]) -> Union[
                    ScraperStorageBackendPairData, List[ScraperStorageBackendPairData]]:
        """ Get currency data from storage for specified scraper.
                IF pair_title is None this method will return list of all aviable
                    currency pairs for specified scraper.
        """
        scraper_obj = await self.get_scraper(scraper)
        data = await self._storage_backend.get_pair_data(
            scraper_obj.EXCHANGER_UNIQ_NAME, pair_title=pair_title)
        if isinstance(data, dict):
            return list(data.values())
        elif not isinstance(data, ScraperStorageBackendPairData):
            raise TypeError(
                "backend storage get method should return scope of ScraperStorageBackendPairData objects")
        return data

    async def get_all(
            self,
            only_for_pair_title: Optional[str],
            group_by_currency_pair: Optional[bool] = True) -> Union[
                Dict[
                    str, ScraperStorageBackendPairData],
                Dict[
                    str, Dict[str, List[ScraperStorageBackendPairData]]]]:
        """
            Get currency data from storage for all aviable scraper in scraping manager flow
                IF group_by_currency_pair is True this method will return dict object
                    like {scraper_exchange_uniq_name: {pair_title: [data1, data2, data3]}}
        """
        scrapers_data = await self._storage_backend.get_all(only_for_pair_title=only_for_pair_title)
        if group_by_currency_pair is True:
            return scrapers_data
        return {
                scraper_name:
                    [
                        pair_data for pair_data in list(scraper_data_dict.values())
                    ] for scraper_name, scraper_data_dict in scrapers_data.items()
            }
