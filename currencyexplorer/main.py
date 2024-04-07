import traceback
import asyncio
from contextlib import asynccontextmanager
from loguru import logger 
from fastapi import FastAPI, Request, HTTPException, status
from app.routers import (
    root,
    explorer
)
from app.scrapers import EXCHANGERS_MAPPING
from .core.exchangers_scraping import ExplorerPairInvalidFormatException
from . import config, scrapers_manager


# Init scrapers for scrapers manager instance and setup worker flow
scrapers_manager.append_to_scrapers(*list(EXCHANGERS_MAPPING.values()))

@asynccontextmanager
async def aplication_flow_lifespan(app: FastAPI):
    """ Pre-Setup aplication method (Startup API and scraper workers together in async loop)
            - Pre-load data before API startup
            - Startup all scraper workers process before API startup
            - Waiting for all worker processes to start before starting API
            - Stop all scraper workers process after API when API shuts down
    """
    logger.info("Scrapers manager: loading currency rates...")
    await scrapers_manager.update_all()
    logger.info("Scrapers manager: currency rates loaded. Ready for work!")
    logger.info("Scrapers manager: setup worker tasks...")
    await scrapers_manager.run_active_updater()
    logger.info("Scrapers manager: check worker status...")
    await asyncio.sleep(config.WAIT_SCRAPER_WORKERS_TIMEOUT)
    scraper_status_mapping = {
        scraper:
            scraper.currency_listener_status async for scraper in scrapers_manager.iter_scrapers(
                ) if scraper.LISTNER_AUTO_START is True}
    if not all(list(scraper_status_mapping.values())):
        try:
            await scrapers_manager.stop_active_updater()
        except Exception as e:
            logger.error(traceback.format_exc())
        raise RuntimeError("Scrapers manager: failed to start scrapers! ({})".format(
            ",".join(
                    [scraper.EXCHANGER_UNIQ_NAME for scraper, s_status in scraper_status_mapping.items(
                    ) if s_status is False]
                )))
    logger.info("Scrapers manager: Application ready for start!")
    yield
    logger.info("Scrapers manager: Sending stop signal to workers...")
    await scrapers_manager.stop_active_updater()
    await asyncio.sleep(config.STOP_SCRAPER_WORKERS_TIMEOUT)
    try:
        loop = asyncio.get_running_loop()
    except Exception as e:
        loop.close()
    logger.info("Scrapers manager: clear!")


# Schema info
tags_metadata = [
    {
        "name": "Root",
        "description": "Basic API",
    },
]


# Init app

description = """

## RestAPI Authentication


## WebSocket Currency Explorer Listener

> You can receive rate data from exchanges using a **WebSocket** as a listener!

### Usage:

The web socket for listening to the course from exchanges is available at the following path:
```
{websocket_endpoint}
```

#### Authentication
> Authorization for working with WebSocket listener repeats RestAPI authorization except that the secret token must be passed directly in the request path (instead of headers values )

Example:
```
{websocket_endpoint_with_auth}
```

#### Using filters:
> It implements exactly the same access interface as the REST API end'point - `{get_currency_info_endpoint}`

#### Update Frequency:
> You can use the documentation of this API method as a source of information on using websocket and what parameters need to be passed for it


#### WebSocket listener timeout limit:
> The application is limited to a maximum connection time of `{max_connection_timeout}` seconds
_____
## ⬇️⬇️⬇️ REST API Docs bellow ⬇️⬇️⬇️



""".format(
    websocket_endpoint_with_auth=explorer.ws_router.url_path_for(
        'connect_to_currency_listener'),
    websocket_endpoint=explorer.ws_router.url_path_for('connect_to_currency_listener'),
    get_currency_info_endpoint=explorer.router.url_path_for('get_currency_info'),
    max_connection_timeout="disabled" if config.WEBSOCKET_UPDATER_CONNECTION_TIMEOUT_LIMIT in (
        0, None, ) else config.WEBSOCKET_UPDATER_CONNECTION_TIMEOUT_LIMIT
)

app = FastAPI(
    title="CurrencyExplorer",
    description=description,
    summary="Test task for Kauri employment process",
    contact={
        "name": "Vladyslav. L",
        "url": "https://t.me/wathipol",
        "email": "v.liubachevskyi@gmail.com",
    },
    openapi_tags=tags_metadata,
    lifespan=aplication_flow_lifespan
)


# Init URLs
app.include_router(root.router)
app.include_router(explorer.router)
app.include_router(explorer.ws_router)


# Init API flow

@app.exception_handler(ExplorerPairInvalidFormatException)
async def unicorn_exception_handler(request: Request, exc: ExplorerPairInvalidFormatException):
    """ Handler for basic pair format validator exception """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=exc.description)