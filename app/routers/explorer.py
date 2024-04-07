import asyncio
import time
from websockets.exceptions import ConnectionClosed
from loguru import logger
from fastapi import WebSocket, Depends, WebSocketDisconnect, Query
from app.utils.base_router import make_base_router
from app.dependencies import get_query_currency_pair, get_query_exchange
from app.schemas.explorer import GetExplorerInfoResponse
from app.utils.explorer import ScraperManagerGetter
from currencyexplorer import config


router = make_base_router("Currency Explorer")
ws_router = make_base_router("Currency Explorer Socket", basic_auth=False, ws_auth=True)


@router.get("/currency")
async def get_currency_info(
        exchange: str | None = Depends(get_query_exchange),
        pair: str | None = Depends(get_query_currency_pair)) -> GetExplorerInfoResponse:
    """ Get current currency rates from one or multiple exchanges """
    return await ScraperManagerGetter(exchange=exchange, pair=pair).get()


@ws_router.websocket("/currency_listener")
async def connect_to_currency_listener(
        websocket: WebSocket,
        exchange: str | None = Depends(get_query_exchange),
        pair: str | None = Depends(get_query_currency_pair),
        frequency_timeout: float | None = Query(...)) -> GetExplorerInfoResponse:
    """ WebSocket listener for currency one or multiple exchange rates
            Params works exactly like `get_currency_info` endpoint method
    """
    await websocket.accept()
    connected_timestamp = time.time()
    
    # Limiter for frequency timeout
    current_frequency_timeout = float(
        config.DEFAULT_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT) if frequency_timeout is None else float(
            frequency_timeout)
    if current_frequency_timeout < config.MIN_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT:
        current_frequency_timeout = float(config.MIN_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT)
    elif current_frequency_timeout > config.MAX_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT:
        current_frequency_timeout = float(config.MAX_WEBSOCKET_UPDATER_FREQUENCY_TIMEOUT)
    
    logger.info("Accepted new websocket listener!")
    response_getter = ScraperManagerGetter(exchange=exchange, pair=pair)
    data = None
    try:
        while True:
            if config.WEBSOCKET_UPDATER_CONNECTION_TIMEOUT_LIMIT not in (0, None, ) and (
                    (time.time() - connected_timestamp
                        ) >= config.WEBSOCKET_UPDATER_CONNECTION_TIMEOUT_LIMIT):
                break
            data = await response_getter.get()
            await websocket.send_json(data.model_dump())
            await asyncio.sleep(current_frequency_timeout)
    except (ConnectionClosed, WebSocketDisconnect):
        pass
    except Exception as e:
        await websocket.close()
