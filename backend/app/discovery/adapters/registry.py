"""Adapter registry — maps source names to adapter classes."""

from typing import Any

from app.discovery.adapters.base import BaseAdapter

_REGISTRY: dict[str, type[BaseAdapter]] = {}


def register(adapter_cls: type[BaseAdapter]) -> type[BaseAdapter]:
    """Decorator to register an adapter class by its source name."""
    if not adapter_cls.source:
        raise ValueError(f"Adapter {adapter_cls.__name__} must define a non-empty `source`")
    _REGISTRY[adapter_cls.source] = adapter_cls
    return adapter_cls


def get(source: str) -> type[BaseAdapter] | None:
    """Return the adapter class for a source, or None if not registered."""
    return _REGISTRY.get(source)


def list_sources() -> list[str]:
    """Return all registered source names."""
    return sorted(_REGISTRY.keys())


def instantiate(source: str, config: dict[str, Any] | None = None) -> BaseAdapter | None:
    """Instantiate the adapter for a source with optional config."""
    cls = get(source)
    if cls is None:
        return None
    return cls(config)