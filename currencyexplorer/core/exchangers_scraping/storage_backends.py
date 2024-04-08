import time
from loguru import logger
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union, Dict, Callable, List
from pydantic import BaseModel, Field, field_validator
from .exceptions import ExplorerPairInvalidFormatException
from abc import ABC, abstractmethod


class ScraperStorageBackendPairData(BaseModel):
    """
        Currency scraper rate response data schema
            This object contain data about currency pair exchange rate on specific exchanging platform
    """
    exchanger_uniq_name: str
    currency_pair_title: str
    currency_rate: Optional[float] = None
    last_update: Optional[float] = Field(default_factory=lambda: time.time())

    @property
    def last_update_datetime(self) -> Optional[datetime]:
        """ Return datetime.datetime object from last_update timestamp data.
                If last_update is None this methos also return NoneType
        """
        return None if self.last_update is None else datetime.fromtimestamp(self.last_update)
    
    @property
    def time_from_last_update(self) -> Optional[float]:
        """ Time that has passed since the data was updated.
                Return NoneType if data is empty
        """
        if self.last_update is None:
            return
        return time.time() - self.last_update

    @field_validator('currency_pair_title', mode="before")
    @classmethod
    def check_currency_pair_title(cls, v: str) -> str:
        return ExplorerPairInvalidFormatException.explorer_pair_format_validator(v)
        

class AbstractScraperStorageBackend(ABC):
    """ Basic storage backend class for exchangers API scrapper method.
            Сhild classes of this should describe the logic for loading/storing cryptocurrency rate data
                from parsing exchanges in a specific storage
    """

    @abstractmethod
    async def store_pair_data(self, new_or_update_data: ScraperStorageBackendPairData) -> None:
        """
            This method should describe store/update currency data to specific storage
        """
        raise NotImplementedError

    async def get_pair_data(
            self,
            exchanger_uniq_name: Optional[str] = None,
            pair_title: Optional[str] = None) -> Union[
                ScraperStorageBackendPairData, Dict[str, ScraperStorageBackendPairData]]:
        """
            This method should describe loading currency data logic from specific storage.
                - IF exchanger_uniq_name is NoneType, it should return all pair from specified exchanger.
                - IF pair_title is NoneType, it should return all data for this exchanger_uniq_name
            
                In both cases it return dict:
                    {exchanger_uniq_name: {pair_title: ScraperStorageBackendPairData}} .
                If specified exchanger and pair this method should return exactly currency data object
        """
        return ScraperStorageBackendPairData(
            exchanger_uniq_name=str(exchanger_uniq_name),
            currency_pair_title=str(pair_title), last_update=None)

    async def get_all(
            self,
            only_for_pair_title: Optional[str] = None) -> Dict[
                str, Dict[str, ScraperStorageBackendPairData]]:
        """ This method should describe loading all currency data from storage.
                It makes sense to override the method only if it is possible to make scraping
                    all data more effictive, for example if it were a SQL database
                        -> Return dict like {exchange: {pair_title: currency_data}}
                            IF only_for_pair_title is True method should return
                                same dict without only_for_pair_title in currency_pair_name
        """
        return await self.get_pair_data(pair_title=only_for_pair_title)


class CurrencyScraperAsyncSafeDictStorage(AbstractScraperStorageBackend):
    """ Currency scraper storage in simple python dict.
            !!! Only for testing or local usage (FakeDB) !!!
    """
    
    def __init__(self, *args, stored_data_lifetime: Optional[float] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stored_data_lifetime = stored_data_lifetime

        # {exchanger_uniq_name: {pair_title: ScraperStorageBackendPairData } }
        self.__fake_dict_storage: Dict[str, Dict[str, ScraperStorageBackendPairData]] = dict()
          
    async def _cleanup_expired_data(self) -> None:
        """
            Cleans up expired data from the internal storage dictionary 
        """
        if self.stored_data_lifetime is None:
            return
        for exchanger_name, exchanger_data in self.__fake_dict_storage.items():
            for pair_title, pair_data in list(exchanger_data.items()):
                if self.stored_data_lifetime == 0 or (
                        self.stored_data_lifetime is not None and (
                            pair_data.time_from_last_update >= self.stored_data_lifetime)):
                    del self.__fake_dict_storage[exchanger_name][pair_title]

    async def store_pair_data(self, new_or_update_data: ScraperStorageBackendPairData) -> None:
        if new_or_update_data.exchanger_uniq_name in self.__fake_dict_storage:
            self.__fake_dict_storage[
                new_or_update_data.exchanger_uniq_name][
                    new_or_update_data.currency_pair_title] = new_or_update_data
            return
        self.__fake_dict_storage[new_or_update_data.exchanger_uniq_name] = {
            new_or_update_data.currency_pair_title: new_or_update_data}
        
        # Clean up expired data after storing
        await self._cleanup_expired_data()

    async def get_pair_data(
            self,
            pair_title: Optional[str],
            exchanger_uniq_name: Optional[str] = None) -> Union[
                ScraperStorageBackendPairData, Dict[str, ScraperStorageBackendPairData]]:
        if exchanger_uniq_name is None:
            return await self.get_all(only_for_pair_title=pair_title)
        
        # Clean up expired data before retrieval
        await self._cleanup_expired_data()

        if exchanger_uniq_name in self.__fake_dict_storage:
            result_from_exchanger = self.__fake_dict_storage[exchanger_uniq_name]
            if pair_title is None:
                # All data record for specified exchanger without passed currency pair title
                return {exchanger_uniq_name: {p_n: p_d for p_n, p_d in result_from_exchanger.items()}}
            pair_result = result_from_exchanger.get(pair_title)
            if pair_result is not None:
                # Currency data from specified exchanger and currency pair title
                return pair_result
        
        # -> Empty result
        data = await super().get_pair_data(
            exchanger_uniq_name=exchanger_uniq_name, pair_title=pair_title)
        return data
    
    async def get_all(
            self, only_for_pair_title: Optional[str] = None) -> Dict[
                str, Dict[str, ScraperStorageBackendPairData]]:
        
        # Clean up expired data before retrieval
        await self._cleanup_expired_data()
        
        data = self.__fake_dict_storage.copy()
        if only_for_pair_title is None:
            return data
        pair_found_in_exchangers = {
            exchanger_name: currency_object
            for exchanger_name, symbol_dict in data.items()
            for symbol, currency_object in symbol_dict.items()
            if symbol == only_for_pair_title
        }

        # Formating valid return object
        response = {}
        for target_exchanger, e_data in pair_found_in_exchangers.items():
            if target_exchanger not in response:
                response[target_exchanger] = {}
            response[target_exchanger][only_for_pair_title] = e_data
        return response
