# services/collector/app/connection/manager.py

import asyncio
import json

import websockets
from websockets.exceptions import ConnectionClosed

from services.collector.app.connection.exceptions import (
    NetworkError,
    PayloadError,
    StaleConnectionError,
)
from services.collector.app.connection.health import HealthStatus
from services.collector.app.connection.heartbeat import HeartbeatMonitor
from services.collector.app.connection.metrics import ConnectionMetrics
from services.collector.app.connection.retry import ExponentialBackoff
from services.collector.app.connection.state import ConnectionState
from services.collector.app.core.config import (
    RECEIVE_TIMEOUT_SECONDS,
    STALE_THRESHOLD_SECONDS,
)
from shared.logging.config import get_logger

# import signal


class ConnectionManager:
    """Manages WebSocket connection lifecycle with automatic reconnection.

    This class handles connecting to a WebSocket stream, receiving messages,
    detecting connection failures, and automatically reconnecting with
    exponential backoff. It monitors connection health via heartbeat detection
    and gracefully handles shutdown signals.
    """

    def __init__(self, stream_url: str):
        """Initialize the connection manager.

        Args:
            stream_url (str): The WebSocket URL to connect to.
        """
        self.stream_url = stream_url

        self.logger = get_logger("connection-manager")

        self.metrics = ConnectionMetrics()

        self.health_status = HealthStatus.HEALTHY

        self.state = ConnectionState.DISCONNECTED

        self.websocket = None

        self.shutdown_event = asyncio.Event()

        self.backoff = ExponentialBackoff()

        self.heartbeat = HeartbeatMonitor(stale_threshold=STALE_THRESHOLD_SECONDS)

    async def connect(self) -> None:
        """Establish a WebSocket connection to the stream URL.

        Sets the connection state to CONNECTING, establishes the WebSocket
        connection with ping/pong health checks, resets the backoff counter,
        and updates the state to CONNECTED on success.

        Raises:
            Exception: Any exception raised by websockets.connect().
        """
        self.state = ConnectionState.CONNECTING

        self.logger.info(f"Connecting to stream: {self.stream_url}")

        self.websocket = await websockets.connect(
            self.stream_url,
            ping_interval=20,
            ping_timeout=20,
        )

        self.state = ConnectionState.CONNECTED

        self.backoff.reset()

        self.logger.info("Connection established")
        self.health_status = HealthStatus.HEALTHY

    async def metrics_reporter(self):
        while not self.shutdown_event.is_set():
            await asyncio.sleep(60)

            self.logger.info(
                (
                    "EVENT=METRICS "
                    f"MESSAGES={self.metrics.messages_received} "
                    f"RECONNECTS={self.metrics.reconnect_count} "
                    f"TIMEOUTS={self.metrics.timeout_count} "
                    f"STALE={self.metrics.stale_events} "
                    f"UPTIME={self.metrics.uptime_seconds:.0f}s "
                    f"HEALTH={self.health_status}"
                )
            )

    async def receive_loop(self) -> None:
        """Continuously receive messages from the WebSocket connection.

        Listens for incoming messages, updates the heartbeat monitor,
        and logs received events. Detects stale connections and raises
        ConnectionError if no messages are received within the timeout period
        and the connection is deemed stale.

        Raises:
            asyncio.TimeoutError: If message reception exceeds timeout.
            ConnectionClosed: If the WebSocket connection is unexpectedly closed.
            ConnectionError: If the connection is detected as stale.
        """
        while not self.shutdown_event.is_set():
            try:
                message = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=RECEIVE_TIMEOUT_SECONDS,
                )

                self.heartbeat.beat()

                try:
                    json.loads(message)

                except json.JSONDecodeError as exc:
                    self.logger.error(f"EVENT=PAYLOAD_ERROR MESSAGE={exc}")
                    continue

                self.metrics.increment_messages()

            except asyncio.TimeoutError:
                self.metrics.increment_timeouts()

                self.logger.warning("EVENT=RECEIVE_TIMEOUT")

                if self.heartbeat.is_stale():
                    self.metrics.increment_stale_events()

                    raise StaleConnectionError(
                        "No messages received within stale threshold."
                    )

            except ConnectionClosed as exc:
                self.logger.warning(f"EVENT=CONNECTION_CLOSED ERROR={exc}")
                raise

    async def reconnect(self) -> None:
        """Wait before attempting to reconnect with exponential backoff.

        Sets the connection state to RECONNECTING, calculates the next
        backoff delay (with jitter), and sleeps for that duration before
        returning control to allow for a reconnection attempt.
        """
        self.state = ConnectionState.RECONNECTING

        delay = self.backoff.next_delay()

        self.logger.warning(f"Reconnecting in {delay:.2f}s")

        self.metrics.increment_reconnects()
        self.logger.warning(
            (f"EVENT=RECONNECT ATTEMPT={self.backoff.attempt} DELAY={delay:.2f}s")
        )
        await asyncio.sleep(delay)

    async def close(self) -> None:
        """Gracefully close the WebSocket connection and stop the manager.

        Sets the shutdown event to signal all loops to stop, closes the
        WebSocket connection if active, and updates the connection state
        to DISCONNECTED.
        """
        self.state = ConnectionState.STOPPING

        self.logger.info("Closing connection")

        self.shutdown_event.set()

        if self.websocket:
            await self.websocket.close()

        self.state = ConnectionState.DISCONNECTED

        self.logger.info("Shutdown complete")

    async def listen(self):
        """Async generator that yields messages from the WebSocket stream.

        Continuously attempts to connect and receive messages from the stream.
        On connection failure or error, automatically reconnects with exponential
        backoff. Yields each message as it arrives.

        Yields:
            dict: Parsed JSON message from the stream.
        """
        # Start metrics reporter as a background task
        reporter_task = asyncio.create_task(self.metrics_reporter())

        try:
            while not self.shutdown_event.is_set():
                try:
                    await self.connect()

                    while not self.shutdown_event.is_set():
                        try:
                            message = await asyncio.wait_for(
                                self.websocket.recv(),
                                timeout=RECEIVE_TIMEOUT_SECONDS,
                            )

                            self.heartbeat.beat()

                            try:
                                parsed_message = json.loads(message)
                                yield parsed_message

                            except json.JSONDecodeError as exc:
                                self.logger.error(f"EVENT=PAYLOAD_ERROR MESSAGE={exc}")
                                continue

                            self.metrics.increment_messages()

                        except asyncio.TimeoutError:
                            self.metrics.increment_timeouts()

                            self.logger.warning("EVENT=RECEIVE_TIMEOUT")

                            if self.heartbeat.is_stale():
                                self.metrics.increment_stale_events()

                                raise StaleConnectionError(
                                    "No messages received within stale threshold."
                                )

                        except ConnectionClosed as exc:
                            self.logger.warning(f"EVENT=CONNECTION_CLOSED ERROR={exc}")
                            raise

                except (
                    ConnectionClosed,
                    OSError,
                    NetworkError,
                    StaleConnectionError,
                    PayloadError,
                ) as exc:
                    self.health_status = HealthStatus.DEGRADED
                    self.logger.error(
                        (
                            f"EVENT=CONNECTION_FAILURE "
                            f"TYPE={type(exc).__name__} "
                            f"MESSAGE={exc}"
                        )
                    )

                    if not self.shutdown_event.is_set():
                        await self.reconnect()
        finally:
            # Ensure reporter task is cancelled on shutdown
            reporter_task.cancel()
            try:
                await reporter_task
            except asyncio.CancelledError:
                pass

    async def run(self) -> None:
        """Main connection lifecycle loop.

        Continuously attempts to connect and receive messages from the stream.
        On connection failure or error, automatically reconnects with exponential
        backoff. Continues until the shutdown event is set.
        """
        async for _ in self.listen():
            pass

    # signal handlers are not implemented on windows platform,
    # so this method is commented out to avoid issues during development on windows

    # def register_signal_handlers(self) -> None:
    #     """Register signal handlers for graceful shutdown.

    #     Registers handlers for SIGINT (Ctrl+C) and SIGTERM signals that
    #     trigger the close() coroutine, allowing graceful shutdown of the
    #     connection manager when receiving termination signals.
    #     """
    #     loop = asyncio.get_running_loop()

    #     for sig in (
    #         signal.SIGINT,
    #         signal.SIGTERM,
    #     ):
    #         loop.add_signal_handler(
    #             sig,
    #             lambda: asyncio.create_task(
    #                 self.close()
    #             ),
    #         )
