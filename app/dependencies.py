from loguru import logger
from currencyexplorer import config
from fastapi import HTTPException, status, Query, WebSocketException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from app.scrapers import EXCHANGERS_MAPPING
from currencyexplorer.core.exchangers_scraping import ExplorerPairInvalidFormatException


api_key_header = HTTPBearer(auto_error=False) # Default header token security


async def get_auth_api_token(credentials: HTTPAuthorizationCredentials = Depends(api_key_header)):
    """ 
        FastAPI Depend for basic api token auth validation (HEADER)
    """
    if credentials is None or str(credentials.credentials) != config.API_AUTHENTICATION_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='could validate api key')
    return str(credentials.credentials)


async def validate_ws_auth_api_token(authorization: str | None = Header(...)):
    """
        FastAPI Depend for HEADER api token basic auth validation in WebSocket connection
    """
    if authorization is None:
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    scheme, _, param = str(authorization).partition(" ")
    if param != config.API_AUTHENTICATION_TOKEN:
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    return param


async def get_query_currency_pair(
        pair: str | None = Query(default=None, example="USDT_BTC")) -> str | None:
    """ Extract and validate pair string from request param """
    if pair is None:
        return
    return ExplorerPairInvalidFormatException.explorer_pair_format_validator(pair)


async def get_query_exchange(
        exchange: str | None = Query(default=None, example="binance")) -> str | None:
    """ Extract and validate exchange uniq name from request param """
    if exchange is None:
        return
    if exchange not in EXCHANGERS_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='passed exchange name({}) not found in a system'.format(exchange))
    return str(exchange)
