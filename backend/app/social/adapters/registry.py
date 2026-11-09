"""Registry for social adapters."""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter

_REGISTRY: dict[str, type[BaseSocialAdapter]] = {}


def register(adapter_cls: type[BaseSocialAdapter]) -> type[BaseSocialAdapter]:
    """Register an adapter class by its platform name."""
    if not adapter_cls.platform:
        raise ValueError(f"Adapter {adapter_cls.__name__} must define a non-empty `platform`")
    _REGISTRY[adapter_cls.platform] = adapter_cls
    return adapter_cls


def get(platform: str) -> type[BaseSocialAdapter] | None:
    """Return the adapter class for a platform, or None."""
    return _REGISTRY.get(platform)


def list_platforms() -> list[str]:
    return sorted(_REGISTRY.keys())


def instantiate(platform: str, config: dict[str, Any] | None = None) -> BaseSocialAdapter | None:
    cls = get(platform)
    if cls is None:
        return None
    return cls(config)
