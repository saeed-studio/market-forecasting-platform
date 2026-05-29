# services/collector/app/connection/heartbeat.py

import time


class HeartbeatMonitor:
    """Monitor connection health by tracking message reception timestamps.

    This class tracks the time of the last received message and can determine
    if the connection has become stale (no messages received within a threshold).
    Useful for detecting hung or dead WebSocket connections.
    """

    def __init__(self, stale_threshold: int = 30):
        """Initialize the heartbeat monitor.

        Args:
            stale_threshold (int): Time in seconds after which a connection
                is considered stale if no messages are received. Defaults to 30.
        """
        self.stale_threshold = stale_threshold
        self.last_message_ts = time.time()

    def beat(self) -> None:
        """Record a heartbeat by updating the last message timestamp.

        This method should be called each time a message is successfully
        received from the WebSocket connection.
        """
        self.last_message_ts = time.time()

    def is_stale(self) -> bool:
        """Check if the connection is stale.

        Returns:
            bool: True if no messages have been received within the stale
                threshold period, False otherwise.
        """
        return (time.time() - self.last_message_ts) > self.stale_threshold
