from currencyexplorer import scrapers_manager
from app.schemas.explorer import GetExplorerInfoResponse


class ScraperManagerGetter:
    """
        Simple wrapper for easy reload value from scraping manager with specified params
    """
    def __init__(self, exchange: str | None, pair: str | None):
        self.exchange = exchange
        self.pair = pair
    
    async def get(self):
        """ Make explorer response from scraping manager """
        data = []
        if self.exchange is not None:
            data = await scrapers_manager.get(scraper=self.exchange, pair_title=self.pair)
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
        return GetExplorerInfoResponse.from_scraper_pair_data_list(data)
