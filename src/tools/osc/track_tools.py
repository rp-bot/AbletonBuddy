"""
Marvin-compatible tools for AbletonOSC Track API - track control and queries.
"""

from __future__ import annotations

from typing import Optional, Union, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_track(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: arm, name, color, color_index, mute, solo, volume, panning, send, available_input_routing_channels, available_input_routing_types, available_output_routing_channels, available_output_routing_types, can_be_armed, current_monitoring_state, fired_slot_index, playing_slot_index, fold_state, has_audio_input, has_audio_output, has_midi_input, has_midi_output, input_routing_channel, input_routing_type, output_routing_channel, output_routing_type, output_meter_left, output_meter_right, output_meter_level, is_foldable, is_grouped, is_visible"
        ),
    ],
    additional_params: Annotated[
        Optional[str],
        Field(description="Additional params (e.g., send_id for send queries)"),
    ] = None,
) -> str:
    """
    Query Track API properties from Ableton Live via AbletonOSC.
    Use query_type like 'arm', 'name', 'volume', 'mute', 'solo', 'panning', 'send', etc.
    For 'send' queries, provide send_id in additional_params.
    """
    osc = OSCClient()
    query_map = {
        # Basic properties
        "arm": "/live/track/get/arm",
        "name": "/live/track/get/name",
        "color": "/live/track/get/color",
        "color_index": "/live/track/get/color_index",
        "mute": "/live/track/get/mute",
        "solo": "/live/track/get/solo",
        "volume": "/live/track/get/volume",
        "panning": "/live/track/get/panning",
        "send": "/live/track/get/send",
        # Routing - available options
        "available_input_routing_channels": "/live/track/get/available_input_routing_channels",
        "available_input_routing_types": "/live/track/get/available_input_routing_types",
        "available_output_routing_channels": "/live/track/get/available_output_routing_channels",
        "available_output_routing_types": "/live/track/get/available_output_routing_types",
        # Routing - current settings
        "input_routing_channel": "/live/track/get/input_routing_channel",
        "input_routing_type": "/live/track/get/input_routing_type",
        "output_routing_channel": "/live/track/get/output_routing_channel",
        "output_routing_type": "/live/track/get/output_routing_type",
        # State and capabilities
        "can_be_armed": "/live/track/get/can_be_armed",
        "current_monitoring_state": "/live/track/get/current_monitoring_state",
        "fired_slot_index": "/live/track/get/fired_slot_index",
        "playing_slot_index": "/live/track/get/playing_slot_index",
        # Audio/MIDI capabilities
        "has_audio_input": "/live/track/get/has_audio_input",
        "has_audio_output": "/live/track/get/has_audio_output",
        "has_midi_input": "/live/track/get/has_midi_input",
        "has_midi_output": "/live/track/get/has_midi_output",
        # Metering
        "output_meter_left": "/live/track/get/output_meter_left",
        "output_meter_right": "/live/track/get/output_meter_right",
        "output_meter_level": "/live/track/get/output_meter_level",
        # Groups
        "fold_state": "/live/track/get/fold_state",
        "is_foldable": "/live/track/get/is_foldable",
        "is_grouped": "/live/track/get/is_grouped",
        "is_visible": "/live/track/get/is_visible",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args = [track_id]
    if additional_params:
        # For send queries, additional_params is the send_id
        try:
            args.append(int(additional_params))
        except ValueError:
            args.append(additional_params)

    result = osc.send_and_wait(address, args)
    if result is None:
        return f"No response for query: {query_type} on track {track_id}"
    return f"Track {track_id} {query_type}: {result}"


def control_track(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    command_type: Annotated[
        str,
        Field(
            description="Command: set_arm, set_name, set_color, set_color_index, set_mute, set_solo, set_volume, set_panning, set_send, set_input_routing_channel, set_input_routing_type, set_output_routing_channel, set_output_routing_type, set_current_monitoring_state, set_fold_state"
        ),
    ],
    value: Annotated[
        Union[str, int, float],
        Field(description="Value for the command (e.g., volume level, name, etc.)"),
    ],
    additional_params: Annotated[
        Optional[str],
        Field(description="Additional params (e.g., send_id for set_send)"),
    ] = None,
) -> str:
    """
    Execute Track API setter commands via AbletonOSC.
    Use command_type like 'set_volume', 'set_mute', 'set_solo', 'set_name', etc.
    For 'set_send', provide send_id in additional_params.
    """
    osc = OSCClient()
    command_map = {
        # Basic controls
        "set_arm": "/live/track/set/arm",
        "set_mute": "/live/track/set/mute",
        "set_solo": "/live/track/set/solo",
        "set_volume": "/live/track/set/volume",
        "set_panning": "/live/track/set/panning",
        "set_send": "/live/track/set/send",
        # Appearance
        "set_name": "/live/track/set/name",
        "set_color": "/live/track/set/color",
        "set_color_index": "/live/track/set/color_index",
        # Routing
        "set_input_routing_channel": "/live/track/set/input_routing_channel",
        "set_input_routing_type": "/live/track/set/input_routing_type",
        "set_output_routing_channel": "/live/track/set/output_routing_channel",
        "set_output_routing_type": "/live/track/set/output_routing_type",
        # State
        "set_current_monitoring_state": "/live/track/set/current_monitoring_state",
        "set_fold_state": "/live/track/set/fold_state",
    }

    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args = [track_id]
    if additional_params and command_type.lower() == "set_send":
        # For set_send: track_id, send_id, value
        try:
            args.append(int(additional_params))
        except ValueError:
            args.append(additional_params)
    args.append(value)

    result = osc.send_and_wait(address, args, timeout=1.0)
    if result is None or result == "OK":
        return f"Command executed: {command_type} on track {track_id} = {value}"
    return f"Command {command_type} on track {track_id} result: {result}"


def query_track_devices(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: num_devices, devices_name, devices_type, devices_class_name"
        ),
    ],
) -> str:
    """
    Query device information on a track via AbletonOSC.
    Use query_type like 'num_devices', 'devices_name', 'devices_type', 'devices_class_name'.
    """
    osc = OSCClient()
    query_map = {
        "num_devices": "/live/track/get/num_devices",
        "devices_name": "/live/track/get/devices/name",
        "devices_type": "/live/track/get/devices/type",
        "devices_class_name": "/live/track/get/devices/class_name",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    result = osc.send_and_wait(address, [track_id])
    if result is None:
        return f"No response for query: {query_type} on track {track_id}"
    return f"Track {track_id} {query_type}: {result}"


def query_track_clips(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: clips_name, clips_length, clips_color, arrangement_clips_name, arrangement_clips_length, arrangement_clips_start_time"
        ),
    ],
) -> str:
    """
    Query all clips on a track (bulk query) via AbletonOSC.
    Use query_type like 'clips_name', 'clips_length', 'clips_color' for session clips,
    or 'arrangement_clips_name', 'arrangement_clips_length', 'arrangement_clips_start_time' for arrangement clips.
    """
    osc = OSCClient()
    query_map = {
        # Session clips
        "clips_name": "/live/track/get/clips/name",
        "clips_length": "/live/track/get/clips/length",
        "clips_color": "/live/track/get/clips/color",
        # Arrangement clips
        "arrangement_clips_name": "/live/track/get/arrangement_clips/name",
        "arrangement_clips_length": "/live/track/get/arrangement_clips/length",
        "arrangement_clips_start_time": "/live/track/get/arrangement_clips/start_time",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    result = osc.send_and_wait(address, [track_id])
    if result is None:
        return f"No response for query: {query_type} on track {track_id}"
    return f"Track {track_id} {query_type}: {result}"


def stop_track_clips(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
) -> str:
    """
    Stop all clips playing on the specified track via AbletonOSC.
    """
    osc = OSCClient()
    result = osc.send_and_wait("/live/track/stop_all_clips", [track_id], timeout=1.0)
    if result is None or result == "OK":
        return f"Stopped all clips on track {track_id}"
    return f"Stop clips on track {track_id} result: {result}"
