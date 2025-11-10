"""
Marvin-compatible tools for AbletonOSC Scene API - scene control and queries.
"""

from __future__ import annotations

from typing import Optional, Union, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_scene(
    scene_id: Annotated[int, Field(description="Scene index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: name, color, color_index, is_empty, is_triggered, tempo, tempo_enabled, time_signature_numerator, time_signature_denominator, time_signature_enabled"
        ),
    ],
) -> str:
    """
    Query Scene API properties from Ableton Live via AbletonOSC.
    Use query_type like 'name', 'color', 'tempo', 'is_empty', etc.
    """
    osc = OSCClient()
    query_map = {
        # Basic properties
        "name": "/live/scene/get/name",
        "color": "/live/scene/get/color",
        "color_index": "/live/scene/get/color_index",
        # State queries
        "is_empty": "/live/scene/get/is_empty",
        "is_triggered": "/live/scene/get/is_triggered",
        # Tempo
        "tempo": "/live/scene/get/tempo",
        "tempo_enabled": "/live/scene/get/tempo_enabled",
        # Time signature
        "time_signature_numerator": "/live/scene/get/time_signature_numerator",
        "time_signature_denominator": "/live/scene/get/time_signature_denominator",
        "time_signature_enabled": "/live/scene/get/time_signature_enabled",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args = [scene_id]

    result = osc.send_and_wait(address, args)
    if result is None:
        return f"No response for query: {query_type} on scene {scene_id}"
    return f"Scene {scene_id} {query_type}: {result}"


def control_scene(
    scene_id: Annotated[int, Field(description="Scene index (0-based)")],
    command_type: Annotated[
        str,
        Field(
            description="Command: fire, fire_as_selected, fire_selected, set_name, set_color, set_color_index, set_tempo, set_tempo_enabled, set_time_signature_numerator, set_time_signature_denominator, set_time_signature_enabled"
        ),
    ],
    value: Annotated[
        Optional[Union[str, int, float]],
        Field(
            description="Value for the command (not needed for fire, fire_as_selected, fire_selected)"
        ),
    ] = None,
) -> str:
    """
    Execute Scene API commands via AbletonOSC.
    Use command_type like 'fire', 'fire_as_selected', 'fire_selected', 'set_name', 'set_tempo', etc.
    Note: fire_selected uses the currently selected scene and doesn't require scene_id in OSC, but we accept it for API consistency.
    """
    osc = OSCClient()
    command_map = {
        # Scene actions
        "fire": "/live/scene/fire",
        "fire_as_selected": "/live/scene/fire_as_selected",
        "fire_selected": "/live/scene/fire_selected",
        # Property setters
        "set_name": "/live/scene/set/name",
        "set_color": "/live/scene/set/color",
        "set_color_index": "/live/scene/set/color_index",
        "set_tempo": "/live/scene/set/tempo",
        "set_tempo_enabled": "/live/scene/set/tempo_enabled",
        "set_time_signature_numerator": "/live/scene/set/time_signature_numerator",
        "set_time_signature_denominator": "/live/scene/set/time_signature_denominator",
        "set_time_signature_enabled": "/live/scene/set/time_signature_enabled",
    }

    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    if command_type.lower() == "fire_selected":
        # fire_selected doesn't require scene_id in OSC (uses currently selected scene)
        # But we accept scene_id for API consistency - just don't send it
        args = []
    elif command_type.lower() in ("fire", "fire_as_selected"):
        # Actions that need scene_id but no value
        args = [scene_id]
    else:
        # Property setters: scene_id, value
        if value is None:
            return f"Value required for command: {command_type}"
        args = [scene_id, value]

    result = osc.send_and_wait(address, args, timeout=1.0)
    if result is None or result == "OK":
        action_desc = f"{command_type}" + (f" = {value}" if value is not None else "")
        return f"Command executed: {action_desc} on scene {scene_id}"
    return f"Command {command_type} on scene {scene_id} result: {result}"
