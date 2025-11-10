"""
Marvin-compatible tools for AbletonOSC Application API - application-level queries and controls.
"""

from __future__ import annotations

from typing import Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_application(
    query_type: Annotated[
        str,
        Field(description="Query type: version, log_level, test"),
    ],
) -> str:
    """
    Query Application API information from Ableton Live via AbletonOSC.
    """

    osc = OSCClient()
    query_map = {
        "version": "/live/application/get/version",
        "log_level": "/live/api/get/log_level",
        "test": "/live/test",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    result = osc.send_and_wait(address, None)
    if result is None:
        return f"No response for query: {query_type}"
    return f"Application {query_type}: {result}"


def control_application(
    command_type: Annotated[
        str,
        Field(description="Command: set_log_level, reload"),
    ],
    value: Annotated[
        str,
        Field(
            description="Value for the command. For set_log_level provide one of: debug, info, warning, error, critical"
        ),
    ]
    | None = None,
) -> str:
    """
    Execute Application API commands via AbletonOSC.
    """

    osc = OSCClient()
    command_map = {
        "set_log_level": "/live/api/set/log_level",
        "reload": "/live/api/reload",
    }

    command = command_type.lower()
    address = command_map.get(command)
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args = []
    if command == "set_log_level":
        if value is None:
            return "Value required: log_level (debug, info, warning, error, critical)"
        if value.lower() not in {"debug", "info", "warning", "error", "critical"}:
            return f"Invalid log level '{value}'. Choose from debug, info, warning, error, critical."
        args.append(value.lower())

    result = osc.send_and_wait(address, args if args else None, timeout=1.0)
    if result is None or result == "OK":
        return f"Command executed: {command_type}" + (
            f" value={value}" if value is not None else ""
        )
    return f"Command {command_type} result: {result}"


__all__ = ["query_application", "control_application"]
