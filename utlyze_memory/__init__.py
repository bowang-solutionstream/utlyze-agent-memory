"""Local source-linked knowledge, observations and inert learning proposals."""
from .store import Memory
from .validation import MemoryError
__all__ = ['Memory', 'MemoryError']
