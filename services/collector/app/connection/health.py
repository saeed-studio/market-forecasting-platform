# services/collector/app/connection/health.py

from enum import Enum


# ✅ With Enum (type-safe)
class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
