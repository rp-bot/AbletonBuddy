"""
Marvin-compatible tools for AbletonOSC Song API - comprehensive session control.
"""

from __future__ import annotations

from typing import Optional, Union, Any, List, Annotated
from pydantic import Field

from tools.osc.client import OSCClient


def query_ableton(
    query_type: Annotated[
        str,
        Field(
            description="Query type: tempo, is_playing, track_names, num_tracks, metronome, current_song_time, loop, signature_numerator, signature_denominator, session_record, arrangement_overdub, back_to_arranger, can_redo, can_undo, clip_trigger_quantization, groove_amount, midi_recording_quantization, nudge_down, nudge_up, punch_in, punch_out, record_mode, session_record_status, song_length"
        ),
    ],
    params: Annotated[
        Optional[str],
        Field(description="Optional comma-separated params for the query"),
    ] = None,
) -> str:
    """
    Query Song API information from Ableton Live via AbletonOSC.
    Use query_type like 'tempo', 'is_playing', 'track_names', 'num_tracks', 'metronome', etc.
    """
    osc = OSCClient()
    query_map = {
        # Core session properties
        "tempo": "/live/song/get/tempo",
        "is_playing": "/live/song/get/is_playing",
        "current_song_time": "/live/song/get/current_song_time",
        "song_length": "/live/song/get/song_length",
        # Track and scene info
        "track_names": "/live/song/get/track_names",
        "num_tracks": "/live/song/get/num_tracks",
        "num_scenes": "/live/song/get/num_scenes",
        # Time signature
        "signature_numerator": "/live/song/get/signature_numerator",
        "signature_denominator": "/live/song/get/signature_denominator",
        # Loop and groove
        "loop": "/live/song/get/loop",
        "loop_start": "/live/song/get/loop_start",
        "loop_length": "/live/song/get/loop_length",
        "groove_amount": "/live/song/get/groove_amount",
        # Recording and overdub
        "session_record": "/live/song/get/session_record",
        "session_record_status": "/live/song/get/session_record_status",
        "arrangement_overdub": "/live/song/get/arrangement_overdub",
        "record_mode": "/live/song/get/record_mode",
        # Metronome and quantization
        "metronome": "/live/song/get/metronome",
        "clip_trigger_quantization": "/live/song/get/clip_trigger_quantization",
        "midi_recording_quantization": "/live/song/get/midi_recording_quantization",
        # History and navigation
        "can_undo": "/live/song/get/can_undo",
        "can_redo": "/live/song/get/can_redo",
        "back_to_arranger": "/live/song/get/back_to_arranger",
        # Punch and nudge
        "punch_in": "/live/song/get/punch_in",
        "punch_out": "/live/song/get/punch_out",
        "nudge_down": "/live/song/get/nudge_down",
        "nudge_up": "/live/song/get/nudge_up",
    }
    address = query_map.get(query_type.lower())
    if not address:
        return f"Unknown query type: {query_type}. Available: {', '.join(sorted(query_map.keys()))}"

    args: List[Any] = []
    if params:
        try:
            args = [p.strip() for p in params.split(",")]
        except Exception:
            args = [params]

    result = osc.send_and_wait(address, args if args else None)
    if result is None:
        return f"No response for query: {query_type}"
    return f"{query_type}: {result}"


def control_ableton(
    command_type: Annotated[
        str,
        Field(
            description="Command: start_playing, stop_playing, continue_playing, set_tempo, set_current_song_time, set_signature_numerator, set_signature_denominator, trigger_session_record, set_session_record, set_arrangement_overdub, set_metronome, set_loop, set_loop_start, set_loop_length, create_midi_track, create_audio_track, create_scene, undo, redo, tap_tempo, capture_midi, create_return_track, delete_scene, delete_return_track, delete_track, duplicate_scene, duplicate_track, jump_by, jump_to_next_cue, jump_to_prev_cue, stop_all_clips, set_back_to_arranger, set_clip_trigger_quantization, set_groove_amount, set_midi_recording_quantization, set_nudge_down, set_nudge_up, set_punch_in, set_punch_out, set_record_mode"
        ),
    ],
    value: Annotated[
        Optional[Union[str, int, float]],
        Field(description="Value for the command (e.g., tempo)"),
    ] = None,
    additional_params: Annotated[
        Optional[str], Field(description="Additional comma-separated params if needed")
    ] = None,
) -> str:
    """
    Execute Song API commands via AbletonOSC.
    Use command_type like 'set_tempo', 'start_playing', 'stop_playing', etc.
    """
    osc = OSCClient()
    command_map = {
        # Playback control
        "start_playing": "/live/song/start_playing",
        "stop_playing": "/live/song/stop_playing",
        "continue_playing": "/live/song/continue_playing",
        "stop_all_clips": "/live/song/stop_all_clips",
        # Tempo and time
        "set_tempo": "/live/song/set/tempo",
        "set_current_song_time": "/live/song/set/current_song_time",
        "tap_tempo": "/live/song/tap_tempo",
        # Time signature
        "set_signature_numerator": "/live/song/set/signature_numerator",
        "set_signature_denominator": "/live/song/set/signature_denominator",
        # Recording and overdub
        "trigger_session_record": "/live/song/trigger_session_record",
        "set_session_record": "/live/song/set/session_record",
        "set_arrangement_overdub": "/live/song/set/arrangement_overdub",
        "set_record_mode": "/live/song/set/record_mode",
        "capture_midi": "/live/song/capture_midi",
        # Metronome and loop
        "set_metronome": "/live/song/set/metronome",
        "set_loop": "/live/song/set/loop",
        "set_loop_start": "/live/song/set/loop_start",
        "set_loop_length": "/live/song/set/loop_length",
        # Groove and quantization
        "set_groove_amount": "/live/song/set/groove_amount",
        "set_clip_trigger_quantization": "/live/song/set/clip_trigger_quantization",
        "set_midi_recording_quantization": "/live/song/set/midi_recording_quantization",
        # Navigation and history
        "undo": "/live/song/undo",
        "redo": "/live/song/redo",
        "set_back_to_arranger": "/live/song/set/back_to_arranger",
        "jump_by": "/live/song/jump_by",
        "jump_to_next_cue": "/live/song/jump_to_next_cue",
        "jump_to_prev_cue": "/live/song/jump_to_prev_cue",
        # Punch and nudge
        "set_punch_in": "/live/song/set/punch_in",
        "set_punch_out": "/live/song/set/punch_out",
        "set_nudge_down": "/live/song/set/nudge_down",
        "set_nudge_up": "/live/song/set/nudge_up",
        # Track and scene management
        "create_midi_track": "/live/song/create_midi_track",
        "create_audio_track": "/live/song/create_audio_track",
        "create_return_track": "/live/song/create_return_track",
        "create_scene": "/live/song/create_scene",
        "delete_track": "/live/song/delete_track",
        "delete_return_track": "/live/song/delete_return_track",
        "delete_scene": "/live/song/delete_scene",
        "duplicate_track": "/live/song/duplicate_track",
        "duplicate_scene": "/live/song/duplicate_scene",
    }
    address = command_map.get(command_type.lower())
    if not address:
        return f"Unknown command type: {command_type}. Available: {', '.join(sorted(command_map.keys()))}"

    args: List[Any] = []
    if value is not None:
        args.append(value)
    if additional_params:
        try:
            # Commands that require integer parameters
            int_param_commands = {
                "create_scene",
                "delete_scene",
                "duplicate_scene",
                "create_midi_track",
                "create_audio_track",
                "delete_track",
                "duplicate_track",
                "delete_return_track",
            }

            params = [p.strip() for p in additional_params.split(",")]

            # Convert to integers for commands that require them
            if command_type.lower() in int_param_commands:
                args.extend([int(p) for p in params])
            else:
                args.extend(params)
        except (ValueError, Exception) as e:
            if isinstance(e, ValueError):
                return f"Error: {command_type} requires integer parameters, but got: {additional_params}"
            args.append(additional_params)

    result = osc.send_and_wait(address, args if args else None, timeout=1.0)
    if result is None or result == "OK":
        return f"Command executed: {command_type}" + (
            f" with value {value}" if value is not None else ""
        )
    return f"Command {command_type} result: {result}"


def test_connection() -> str:
    """
    Test the AbletonOSC connection by calling /live/test
    """
    osc = OSCClient()
    result = osc.send_and_wait("/live/test", timeout=3.0)
    if result is None:
        return "No response from Ableton Live. Ensure Live is running and AbletonOSC is enabled in Preferences > Link/Tempo/MIDI."
    return f"✓ Connected to Ableton Live: {result}"
