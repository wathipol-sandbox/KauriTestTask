from fastapi import APIRouter, Depends
from fastapi import Header, Body
from currencyexplorer import config
from app.utils.base_router import make_base_router
from app.scrapers import EXCHANGERS_MAPPING
from app.schemas.root import AviableExchangesResponse


router = make_base_router("Root")


@router.get("/aviable_exchanges")
async def get_aviable_exchanges_list() -> AviableExchangesResponse:
    return AviableExchangesResponse(result=list(EXCHANGERS_MAPPING.keys()))
