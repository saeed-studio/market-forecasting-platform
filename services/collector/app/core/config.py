# services/collector/app/connection/state.py

BINANCE_TRADES_STREAM = "wss://fstream.binance.com/ws/btcusdt@trade"
# BINANCE_KLINE_1M_STREAM = "wss://fstream.binance.com/ws/btcusdt@kline_1m" # future cline data wont work with iohttp lib
BINANCE_KLINE_1M_STREAM = (
    "wss://data-stream.binance.vision/ws/btcusdt@kline_1m"  # spot url
)

STALE_THRESHOLD_SECONDS = 30
RECEIVE_TIMEOUT_SECONDS = 10

# REST endpoints
FUNDING_RATE_ENDPOINT = "https://fapi.binance.com/fapi/v1/premiumIndex"
OPEN_INTEREST_ENDPOINT = "https://fapi.binance.com/fapi/v1/openInterest"

# Checkpoint database
CHECKPOINT_DB_PATH = "data/checkpoints.db"

# Default symbol (can be changed via env)
DEFAULT_SYMBOL = "BTCUSDT"
