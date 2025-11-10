"""
Marvin-compatible tools for AbletonOSC Clip API - clip control and queries.
"""

from __future__ import annotations

from typing import Optional, Union, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_clip(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    clip_id: Annotated[int, Field(description="Clip index (0-based)")],
    query_type: Annotated[
        str,
        Field(
            description="Query type: name, color, gain, length, file_path, is_audio_clip, is_midi_clip, is_playing, is_recording, playing_position, pitch_coarse, pitch_fine, loop_start, loop_end, start_marker, end_marker, warping, notes"
        ),
    ],
    additional_params: Annotated[
        Optional[str],
        Field(
            description="Additional params (e.g., range parameters for notes query: start_pitch,pitch_span,start_time,time_span)"
        ),
    ] = None,
) -> str:
    """
    Query Clip API properties from Ableton Live via AbletonOSC.
    Use query_type like 'name', 'color', 'gain', 'length', 'is_playing', etc.
    For 'notes' queries, optionally provide range parameters in additional_params as comma-separated: start_pitch,pitch_span,start_time,time_span
    """
    osc = OSCClient()
    query_map = {
        # Basic properties
        "name": "/live/clip/get/name",
        "color": "/live/clip/get/color",
        "gain": "/live/clip/get/gain",
        "length": "/live/clip/get/length",
        "file_path": "/live/clip/get/file_path",
        # Type queries
        "is_audio_clip": "/live/clip/get/is_audio_clip",
        "is_midi_clip": "/live/clip/get/is_midi_clip",
        # State queries
        "is_playing": "/live/clip/get/is_playing",
        "is_recording": "/live/clip/get/is_recording",
        "playing_position": "/live/clip/get/playing_position",
        # Pitch
        "pitch_coarse": "/live/clip/get/pitch_coarse",
        "pitch_fine": "/live/clip/get/pitch_fine",
        # Loop and markers
        "loop_start": "/live/clip/get/loop_start",
        "loop_end": "/live/clip/get/loop_end",
        "start_marker": "/live/clip/get/start_marker",
        "end_marker": "/live/clip/get/end_marker",
        # Warping
        "warping": "/live/clip/get/warping",
        # Notes
        "notes": "/live/clip/get/notes",
    }

    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args = [track_id, clip_id]

    # For notes queries, add optional range parameters
    if query_type.lower() == "notes" and additional_params:
        try:
            # Parse comma-separated range parameters: start_pitch, pitch_span, start_time, time_span
            range_params = [p.strip() for p in additional_params.split(",")]
            for param in range_params:
                try:
                    args.append(float(param))
                except ValueError:
                    args.append(param)
        except Exception:
            # If parsing fails, just append as-is
            args.append(additional_params)

    result = osc.send_and_wait(address, args)
    if result is None:
        return (
            f"No response for query: {query_type} on track {track_id}, clip {clip_id}"
        )
    return f"Track {track_id}, Clip {clip_id} {query_type}: {result}"


def control_clip(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    clip_id: Annotated[int, Field(description="Clip index (0-based)")],
    command_type: Annotated[
        str,
        Field(
            description="Command: fire, stop, duplicate_loop, set_name, set_color, set_gain, set_pitch_coarse, set_pitch_fine, set_loop_start, set_loop_end, set_warping, set_start_marker, set_end_marker, add_notes, remove_notes"
        ),
    ],
    value: Annotated[
        Optional[Union[str, int, float]],
        Field(
            description="Value for the command (not needed for fire, stop, duplicate_loop). For add_notes, provide note data."
        ),
    ] = None,
    additional_params: Annotated[
        Optional[str],
        Field(
            description="Additional params (e.g., note data for add_notes, range params for remove_notes)"
        ),
    ] = None,
) -> str:
    """
    Execute Clip API commands via AbletonOSC.
    Use command_type like 'fire', 'stop', 'set_name', 'set_gain', etc.
    For 'add_notes', provide note data in value or additional_params (format: pitch,start_time,duration,velocity,mute for each note, comma-separated).
    For 'remove_notes', optionally provide range parameters in additional_params: start_pitch,pitch_span,start_time,time_span
    """
    osc = OSCClient()
    command_map = {
        # Playback actions (no value needed)
        "fire": "/live/clip/fire",
        "stop": "/live/clip/stop",
        "duplicate_loop": "/live/clip/duplicate_loop",
        # Property setters
        "set_name": "/live/clip/set/name",
        "set_color": "/live/clip/set/color",
        "set_gain": "/live/clip/set/gain",
        "set_pitch_coarse": "/live/clip/set/pitch_coarse",
        "set_pitch_fine": "/live/clip/set/pitch_fine",
        "set_loop_start": "/live/clip/set/loop_start",
        "set_loop_end": "/live/clip/set/loop_end",
        "set_warping": "/live/clip/set/warping",
        "set_start_marker": "/live/clip/set/start_marker",
        "set_end_marker": "/live/clip/set/end_marker",
        # Notes operations
        "add_notes": "/live/clip/add/notes",
        "remove_notes": "/live/clip/remove/notes",
    }

    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args = [track_id, clip_id]

    if command_type.lower() in ("fire", "stop", "duplicate_loop"):
        # Actions that don't need value parameter
        pass
    elif command_type.lower() == "add_notes":
        # Add notes: track_id, clip_id, pitch, start_time, duration, velocity, mute, ...
        # Parse note data from value or additional_params
        note_data = (
            additional_params if additional_params else (str(value) if value else "")
        )
        if not note_data:
            return f"Note data required for command: {command_type}. Format: pitch,start_time,duration,velocity,mute (comma-separated for multiple notes)"

        try:
            # Parse comma-separated note parameters
            # Each note: pitch, start_time, duration, velocity, mute
            note_params = [p.strip() for p in note_data.split(",")]
            for param in note_params:
                try:
                    # Try to convert to appropriate type
                    if "." in param:
                        args.append(float(param))
                    else:
                        args.append(int(param))
                except ValueError:
                    # If it's a boolean string
                    if param.lower() in ("true", "false", "1", "0"):
                        args.append(param.lower() in ("true", "1"))
                    else:
                        args.append(param)
        except Exception as e:
            return f"Error parsing note data: {e}. Format: pitch,start_time,duration,velocity,mute (comma-separated)"
    elif command_type.lower() == "remove_notes":
        # Remove notes: track_id, clip_id, [start_pitch?, pitch_span?, start_time?, time_span?]
        # If no range specified, remove all notes (empty args after track_id, clip_id)
        if additional_params:
            try:
                # Parse comma-separated range parameters
                range_params = [p.strip() for p in additional_params.split(",")]
                for param in range_params:
                    try:
                        args.append(float(param))
                    except ValueError:
                        args.append(param)
            except Exception:
                args.append(additional_params)
        # If no additional_params, args stays as [track_id, clip_id] which removes all notes
    else:
        # Property setters: track_id, clip_id, value
        if value is None:
            return f"Value required for command: {command_type}"
        args.append(value)

    result = osc.send_and_wait(address, args, timeout=1.0)
    if result is None or result == "OK":
        action_desc = f"{command_type}" + (f" = {value}" if value is not None else "")
        return f"Command executed: {action_desc} on track {track_id}, clip {clip_id}"
    return (
        f"Command {command_type} on track {track_id}, clip {clip_id} result: {result}"
    )
