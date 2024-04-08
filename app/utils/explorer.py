from loguru import logger
from currencyexplorer import scrapers_manager
from app.schemas.explorer import GetExplorerInfoResponse


class ScraperManagerGetter:
    """
        Simple wrapper adapter util for easy reload value from scraping manager with specified params
    """
    def __init__(
            self, exchange: str | None, pair: str | None,
            update_atemp_if_not_exist: bool | None = True):
        self.exchange = exchange
        self.pair = pair
        self.update_atemp_if_not_exist = update_atemp_if_not_exist
        self.update_atemp_if_not_all_source = True
    
    async def get(self, skip_update_atemp: bool | None = False):
        """ Make explorer response from scraping manager """
        data = []
        if self.exchange is not None:
            results = await scrapers_manager.get(scraper=self.exchange, pair_title=self.pair)
            if isinstance(results, (list, tuple, )):
                data.extend(results)
            elif isinstance(results, dict):
                data.extend([p_list for p_list in results.values()])
            else:
                data = [results]
        else:
            data_from_all_exchange = await scrapers_manager.get_all(
                group_by_currency_pair=False, only_for_pair_title=self.pair)
            for p_data in list(data_from_all_exchange.values()):
                if isinstance(p_data, (list, tuple,)):
                    data.extend(p_data)
                else:
                    data.append(p_data)
        if not isinstance(data, (list, tuple, )):
            data = [data]
        
        # Update atemp
        if (len(data) == 0 or (len(data) == 1 and data[0].currency_rate is None)
                ) and self.update_atemp_if_not_exist is True:
            if skip_update_atemp is True:
                logger.info("{}: {} not found in {} exchange, update atemp Failed!".format(
                    self.__class__.__name__, self.pair, self.exchange
                ))
            else:
                logger.info("{}: {} not found in {} exchange! Update atemp...".format(
                    self.__class__.__name__, self.pair, self.exchange
                ))
                if self.exchange is not None:
                    await scrapers_manager.update_from_scraper(self.exchange, pair_title=self.pair)
                else:
                    await scrapers_manager.update_all(pair_title=self.pair)
                return await self.get(skip_update_atemp=True)
        
        elif len(data) > 0 and len(data) < scrapers_manager.scrapers_count and (
                self.update_atemp_if_not_all_source is True and self.update_atemp_if_not_exist is True):
            if skip_update_atemp is True:
                logger.info("{}: not all sources has data, but update atemp failed!".format(
                        self.__class__.__name__))
            else:
                logger.info("{}: not all sources has data, update atemp...".format(
                        self.__class__.__name__))
                if self.exchange is not None:
                    await scrapers_manager.update_from_scraper(self.exchange, pair_title=self.pair)
                else:
                    await scrapers_manager.update_all(pair_title=self.pair)
                return await self.get(skip_update_atemp=True)
        
        return GetExplorerInfoResponse.from_scraper_pair_data_list(data)
