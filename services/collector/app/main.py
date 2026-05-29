# services/collector/app/connection/main.py

import asyncio

from app.connection.manager import ConnectionManager
from app.core.config import BINANCE_TRADES_STREAM


async def main():
    manager = ConnectionManager(stream_url=BINANCE_TRADES_STREAM)

    # manager.register_signal_handlers()

    try:
        await manager.run()

    except KeyboardInterrupt:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
