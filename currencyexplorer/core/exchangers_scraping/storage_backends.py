from loguru import logger
import time
from datetime import datetime
from typing import Optional, Union, Dict
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
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # {exchanger_uniq_name: {pair_title: ScraperStorageBackendPairData } }
        self.__fake_dict_storage: Dict[str, Dict[str, ScraperStorageBackendPairData]] = dict()

    async def store_pair_data(self, new_or_update_data: ScraperStorageBackendPairData) -> None:
        if new_or_update_data.exchanger_uniq_name in self.__fake_dict_storage:
            self.__fake_dict_storage[
                new_or_update_data.exchanger_uniq_name][
                    new_or_update_data.currency_pair_title] = new_or_update_data
            return
        self.__fake_dict_storage[new_or_update_data.exchanger_uniq_name] = {
            new_or_update_data.currency_pair_title: new_or_update_data}

    async def get_pair_data(
            self, exchanger_uniq_name: str, pair_title: Optional[str]) -> Union[
                ScraperStorageBackendPairData, Dict[str, ScraperStorageBackendPairData]]:
        if exchanger_uniq_name in self.__fake_dict_storage:
            result_from_exchanger = self.__fake_dict_storage[exchanger_uniq_name]
            if pair_title is None:
                # All data record for specified exchanger without passed currency pair title
                return result_from_exchanger
            pair_result = result_from_exchanger.get(pair_title)
            if pair_result is not None:
                # Currency data from specified exchanger and currency pair title
                return pair_result
        
        # -> Empty result
        data = await super().get_pair_data(
            pair_title, exchanger_uniq_name)
        return data
    
    async def get_all(
            self, only_for_pair_title: Optional[str] = None) -> Dict[
                str, Dict[str, ScraperStorageBackendPairData]]:
        data = self.__fake_dict_storage.copy()
        if only_for_pair_title is None:
            return data
        logger.info(data)
        return {
            exchanger_uniq_name:
                pair_dict for exchanger_uniq_name, pair_dict in data.items(
                    ) if all(
                        [pair_name == only_for_pair_title for pair_name, pair_data in pair_dict.items()])
        }
