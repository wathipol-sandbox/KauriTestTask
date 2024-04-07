import os
from .settings import ConfigConstructorMapper
from .core.exchangers_scraping import *
from binance.client import Client, AsyncClient


# Detect and load config object
ENVIRONMENT_NAME = str(os.getenv("ENVIRONMENT", "DEV"))
CONFIG_LOADER = ConfigConstructorMapper(ENVIRONMENT_NAME)
config = CONFIG_LOADER()


# Init currency rate scrapers manager instance
scrapers_manager = ExchangersScrapingManager(
    [],
    storage_backend=CurrencyScraperAsyncSafeDictStorage(
        stored_data_lifetime=config.STORED_DATA_LIFETIME_FOR_UPDATE_ATEMP))


# Init binance API SDK
binance_async_client = AsyncClient()
