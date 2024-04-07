from typing import Optional, List
from currencyexplorer.core.exchangers_scraping import ScraperStorageBackendPairData
from pydantic import BaseModel, Field


class ExplorerInfoExchangesNestedBlock(BaseModel):
    exchange: str = Field(descrption="Exchange source name", example="binance")
    currency_rate: float | None = Field(
        default=None, description="Average rate (sale/buy)", example=0.2)
    last_update_timestamp: Optional[float] = Field(
        default=None, description="Unix-time timestamp when last updated", example=1712448799.8908942)


class ExplorerInfoPairsNestedBlock(BaseModel):
    pair_name: str = Field(description="Currency pair name", example="USDT_BTC")
    exchanges: List[ExplorerInfoExchangesNestedBlock] = Field(
        default=[], example=[
            ExplorerInfoExchangesNestedBlock(
                exchange="binance",
                currency_rate=0.000015,
                last_update_timestamp=1712448799.8908942)
        ])


class GetExplorerInfoResponse(BaseModel):
    result: Optional[List[ExplorerInfoPairsNestedBlock]] = Field(
        default=[],
        example=[
            {
                "pair_name": "USDT_BTC",
                "exchanges": [
                    {
                        "exchange": "binance",
                        "currency_rate": 0.000014,
                        "last_update_timestamp": 1712455578.4499707
                    }
                ]
            }
        ])

    @classmethod
    def from_scraper_pair_data_list(
            CLS, pair_data_list: List[ScraperStorageBackendPairData]) -> "GetExplorerInfoResponse":
        """
            Make explorer info response object from list of scrapers response object
        """
        result = []
        exchange_data_map = {}

        # Group exchange data by currency pair
        for pair_data in pair_data_list:
            exchanges = exchange_data_map.setdefault(pair_data.currency_pair_title, [])
            exchanges.append(ExplorerInfoExchangesNestedBlock(
                exchange=pair_data.exchanger_uniq_name,
                currency_rate=pair_data.currency_rate,
                last_update_timestamp=pair_data.last_update
            ))

        # Create ExplorerInfoPairsNestedBlock for each currency pair
        for pair_name, exchanges in exchange_data_map.items():
            result.append(ExplorerInfoPairsNestedBlock(
                pair_name=pair_name,
                exchanges=exchanges
            ))

        return GetExplorerInfoResponse(result=result)