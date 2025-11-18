"""
Marvin-compatible tools for AbletonOSC Device Loader API.
"""

from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field

from tools.osc.client import OSCClient


def _send_device_loader_command(address: str, args: Optional[list] = None) -> str:
    osc = OSCClient()
    result = osc.send_and_wait(address, args or None, timeout=2.0)
    if result is None:
        return f"No response from {address}"
    if isinstance(result, (list, tuple)):
        return f"{address.split('/')[-1]}: {result}"
    return str(result)


def load_device(
    device_name: Annotated[
        str, Field(description="Device name to load onto the selected track.")
    ]
) -> str:
    """
    Load a device from Ableton's browser onto the currently selected track.
    """

    return _send_device_loader_command("/live/device_loader/load", [device_name])


def search_device(
    device_name: Annotated[
        str, Field(description="Device name or partial name to search for.")
    ]
) -> str:
    """
    Search the Device Loader cache for a device.
    """

    return _send_device_loader_command("/live/device_loader/search", [device_name])


def rebuild_device_cache() -> str:
    """
    Rebuild the Device Loader cache by scanning Ableton's browser categories.
    """

    return _send_device_loader_command("/live/device_loader/rebuild_cache")


def get_device_cache_size() -> str:
    """
    Get the number of devices currently cached by the Device Loader.
    """

    return _send_device_loader_command("/live/device_loader/get_cache_size")


def test_load_device(
    device_name: Annotated[
        Optional[str],
        Field(
            description="Optional device name for test loads. Defaults to Operator if omitted."
        ),
    ] = None
) -> str:
    """
    Perform a test load operation without altering the Live set (useful for validation).
    """

    args = [device_name] if device_name else None
    return _send_device_loader_command("/live/device_loader/test_load", args)


__all__ = [
    "load_device",
    "search_device",
    "rebuild_device_cache",
    "get_device_cache_size",
    "test_load_device",
]

