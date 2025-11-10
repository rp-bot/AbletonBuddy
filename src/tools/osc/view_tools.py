"""
Marvin-compatible tools for AbletonOSC View API - selection control and queries.
"""

from __future__ import annotations

from typing import Optional, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_view(
    query_type: Annotated[
        str,
        Field(
            description="Query type: selected_scene, selected_track, selected_clip, selected_device"
        ),
    ],
) -> str:
    """
    Query View API selection state from Ableton Live via AbletonOSC.
    """

    osc = OSCClient()
    query_map = {
        "selected_scene": "/live/view/get/selected_scene",
        "selected_track": "/live/view/get/selected_track",
        "selected_clip": "/live/view/get/selected_clip",
        "selected_device": "/live/view/get/selected_device",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    result = osc.send_and_wait(address, None)
    if result is None:
        return f"No response for query: {query_type}"
    return f"View {query_type}: {result}"


def control_view(
    command_type: Annotated[
        str,
        Field(
            description="Command: set_selected_scene, set_selected_track, set_selected_clip, set_selected_device, start_listen_selected_scene, stop_listen_selected_scene, start_listen_selected_track, stop_listen_selected_track"
        ),
    ],
    value: Annotated[
        Optional[str],
        Field(
            description="Value for the command. For set commands provide necessary indices (comma-separated for clip/device)."
        ),
    ] = None,
) -> str:
    """
    Execute View API commands via AbletonOSC.
    """

    osc = OSCClient()
    command_map = {
        "set_selected_scene": "/live/view/set/selected_scene",
        "set_selected_track": "/live/view/set/selected_track",
        "set_selected_clip": "/live/view/set/selected_clip",
        "set_selected_device": "/live/view/set/selected_device",
        "start_listen_selected_scene": "/live/view/start_listen/selected_scene",
        "stop_listen_selected_scene": "/live/view/stop_listen/selected_scene",
        "start_listen_selected_track": "/live/view/start_listen/selected_track",
        "stop_listen_selected_track": "/live/view/stop_listen/selected_track",
    }

    command = command_type.lower()
    address = command_map.get(command)
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args: list[int] = []

    if command.startswith("set_selected"):
        if value is None:
            return f"Value required for command: {command_type}"

        try:
            parts = [int(part.strip()) for part in str(value).split(",")]
        except ValueError:
            return f"Invalid value '{value}' for command: {command_type}. Provide integer indices."

        if command in {"set_selected_scene", "set_selected_track"}:
            if len(parts) != 1:
                return f"Command {command_type} expects a single index value."
            args = parts
        elif command == "set_selected_clip":
            if len(parts) != 2:
                return "set_selected_clip requires 'track_index,scene_index'"
            args = parts
        elif command == "set_selected_device":
            if len(parts) != 2:
                return "set_selected_device requires 'track_index,device_index'"
            args = parts
    else:
        # start/stop listen commands take no arguments
        args = []

    result = osc.send_and_wait(address, args if args else None, timeout=1.0)
    if result is None or result == "OK":
        return f"Command executed: {command_type}" + (
            f" value={value}" if value is not None else ""
        )
    return f"Command {command_type} result: {result}"


__all__ = ["query_view", "control_view"]
