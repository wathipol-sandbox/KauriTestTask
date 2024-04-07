from typing import List
from pydantic import BaseModel


class AviableExchangesResponse(BaseModel):
    result: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {"result": ["binance", "kraken"]}
        }
    }