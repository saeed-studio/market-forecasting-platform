# services/collector/app/consumers/funding_consumer.py

"""this file defines the FundingConsumer class, which is an async iterator that fetches funding data from
Binance every 60 seconds. It uses aiohttp for asynchronous HTTP requests and generates FundingEvent objects
based on the fetched data."""

import asyncio
import aiohttp
import time
from typing import AsyncIterator
from shared.logging.config import get_logger

from ..schemas.funding import FundingEvent

logger = get_logger(__name__)


class FundingConsumer:
    """
    Async iterator that fetches funding data every 60 seconds.
    """

    def __init__(
        self,
        symbol: str,
        exchange: str = "binance",
        endpoint: str = "https://fapi.binance.com/fapi/v1/premiumIndex",
    ):
        self.symbol = symbol
        self.exchange = exchange
        self.endpoint = endpoint
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def _fetch_one(self) -> FundingEvent:
        """Fetches a single funding event from the API and constructs a FundingEvent object."""
        await self._ensure_session()
        params = {"symbol": self.symbol}
        async with self._session.get(self.endpoint, params=params) as resp:
            resp.raise_for_status()  # Will raise an exception for HTTP errors
            data = await resp.json()

        # Fallback to current time if API doesn't provide it
        event_time = data.get("time") or int(time.time() * 1000)
        funding_rate = float(data["lastFundingRate"])
        mark_price = float(data["markPrice"])

        return FundingEvent(
            event_id=f"{self.symbol}_{event_time}",
            symbol=self.symbol,
            exchange=self.exchange,
            event_time=event_time,
            schema_version=1,
            funding_rate=funding_rate,
            mark_price=mark_price,
        )

    async def stream(self) -> AsyncIterator[FundingEvent]:
        """Continuous async generator – yields one event every 60 seconds."""
        while True:
            try:
                event = await self._fetch_one()
                yield event
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Funding stream error: {e}")
                await asyncio.sleep(60)

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
