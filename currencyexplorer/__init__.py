import os
from .settings import ConfigConstructorMapper
from .core.exchangers_scraping import *


# Detect and load config object
ENVIRONMENT_NAME = str(os.getenv("ENVIRONMENT", "DEV"))
CONFIG_LOADER = ConfigConstructorMapper(ENVIRONMENT_NAME)
config = CONFIG_LOADER()


# Init currency rate scrapers manager instance
scrapers_manager = ExchangersScrapingManager([])
