# servces/collector/app/consumers/oi_consumer.py

import asyncio
import aiohttp
import time
from typing import AsyncIterator
from shared.logging.config import get_logger

from ..schemas.oi import OpenInterestEvent

logger = get_logger(__name__)


class OpenInterestConsumer:
    def __init__(
        self,
        symbol: str,
        exchange: str = "binance",
        endpoint: str = "https://fapi.binance.com/fapi/v1/openInterest",
    ):
        self.symbol = symbol
        self.exchange = exchange
        self.endpoint = endpoint
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def _fetch_one(self) -> OpenInterestEvent:
        await self._ensure_session()
        params = {"symbol": self.symbol}
        async with self._session.get(self.endpoint, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

        event_time = data.get("time") or int(time.time() * 1000)
        open_interest = float(data["openInterest"])

        return OpenInterestEvent(
            event_id=f"{self.symbol}_{event_time}",
            symbol=self.symbol,
            exchange=self.exchange,
            event_time=event_time,
            schema_version=1,
            open_interest=open_interest,
        )

    async def stream(self) -> AsyncIterator[OpenInterestEvent]:
        while True:
            try:
                event = await self._fetch_one()
                yield event
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"OI stream error: {e}")
                await asyncio.sleep(60)

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
