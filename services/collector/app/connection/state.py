# services/collector/app/connection/state.py
"""Connection state enumeration for WebSocket connection lifecycle."""

from enum import Enum


class ConnectionState(str, Enum):
    """Enumeration of possible WebSocket connection states.

    Represents the various states a WebSocket connection can be in during
    its lifecycle, from initial disconnection through connection, potential
    reconnection attempts, to final shutdown.

    Attributes:
        DISCONNECTED: Connection is closed or not yet established.
        CONNECTING: Active attempt to establish a new connection.
        CONNECTED: Connection is established and operational.
        RECONNECTING: Connection was lost, waiting to retry.
        STOPPING: Connection is shutting down gracefully.
    """

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    STOPPING = "STOPPING"
