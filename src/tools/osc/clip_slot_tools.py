"""
Marvin-compatible tools for AbletonOSC Clip Slot API - slot control and queries.
"""

from __future__ import annotations

from typing import Optional, Union, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_clip_slot(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    clip_index: Annotated[int, Field(description="Clip slot index (0-based)")],
    query_type: Annotated[
        str,
        Field(description="Query type: has_clip, has_stop_button"),
    ],
) -> str:
    """
    Query Clip Slot API properties from Ableton Live via AbletonOSC.
    Use query_type like 'has_clip' or 'has_stop_button'.
    """
    osc = OSCClient()
    query_map = {
        "has_clip": "/live/clip_slot/get/has_clip",
        "has_stop_button": "/live/clip_slot/get/has_stop_button",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args = [track_id, clip_index]
    result = osc.send_and_wait(address, args)
    if result is None:
        return f"No response for query: {query_type} on track {track_id}, slot {clip_index}"
    return f"Track {track_id}, Slot {clip_index} {query_type}: {result}"


def control_clip_slot(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    clip_index: Annotated[int, Field(description="Clip slot index (0-based)")],
    command_type: Annotated[
        str,
        Field(
            description="Command: fire, create_clip, delete_clip, set_has_stop_button, duplicate_clip_to"
        ),
    ],
    value: Annotated[
        Optional[Union[int, float, str]],
        Field(
            description="Value for the command. For create_clip: length (beats). For set_has_stop_button: 1 or 0. For duplicate_clip_to: provide 'target_track_index,target_clip_index' in additional_params."
        ),
    ] = None,
    additional_params: Annotated[
        Optional[str],
        Field(
            description="Additional params. For duplicate_clip_to: 'target_track_index,target_clip_index'"
        ),
    ] = None,
) -> str:
    """
    Execute Clip Slot API commands via AbletonOSC.
    fire: toggle play/pause of the specified slot
    create_clip: requires length (beats)
    delete_clip: deletes the clip in the slot
    set_has_stop_button: 1=on, 0=off
    duplicate_clip_to: requires target_track_index,target_clip_index in additional_params
    """
    osc = OSCClient()
    command_map = {
        "fire": "/live/clip_slot/fire",
        "create_clip": "/live/clip_slot/create_clip",
        "delete_clip": "/live/clip_slot/delete_clip",
        "set_has_stop_button": "/live/clip_slot/set/has_stop_button",
        "duplicate_clip_to": "/live/clip_slot/duplicate_clip_to",
    }

    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args = [track_id, clip_index]

    if command_type.lower() == "fire":
        pass
    elif command_type.lower() == "create_clip":
        if value is None:
            return "Value required: length (beats) for create_clip"
        args.append(value)
    elif command_type.lower() == "delete_clip":
        pass
    elif command_type.lower() == "set_has_stop_button":
        if value is None:
            return "Value required: has_stop_button (1 or 0)"
        args.append(value)
    elif command_type.lower() == "duplicate_clip_to":
        if not additional_params:
            return "additional_params required: 'target_track_index,target_clip_index'"
        try:
            target_track_str, target_clip_str = [
                p.strip() for p in additional_params.split(",")
            ]
            args.extend([int(target_track_str), int(target_clip_str)])
        except Exception:
            return "Invalid additional_params for duplicate_clip_to. Use 'target_track_index,target_clip_index'"

    result = osc.send_and_wait(address, args, timeout=1.0)
    if result is None or result == "OK":
        return (
            f"Command executed: {command_type} on track {track_id}, slot {clip_index}"
            + (f" value={value}" if value is not None else "")
        )
    return f"Command {command_type} on track {track_id}, slot {clip_index} result: {result}"
