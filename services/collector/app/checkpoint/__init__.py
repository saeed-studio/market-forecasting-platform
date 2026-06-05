# services/collector/app/checkpoint/__init__.py

from .store import CollectorCheckpointStore

# Explicitly define the public API of this module.
# Only CollectorCheckpointStore will be imported when using 'from checkpoint import *'
# this helps with easier imports --
# import checkpoint.CollectorCheckpointStore instead of checkpoint.store.CollectorCheckpointStore
__all__ = ["CollectorCheckpointStore"]
