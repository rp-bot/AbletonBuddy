"""
Task orchestration utilities for Ableton agents.
"""

from typing import Dict, List

from marvin import Task

from tools.osc.clip_tools import control_clip, query_clip
from tools.osc.device_tools import control_device, query_device
from tools.osc.scene_tools import control_scene, query_scene
from tools.osc.song_tools import control_ableton, query_ableton, test_connection
from tools.osc.track_tools import (
    control_track,
    query_track,
    query_track_clips,
    query_track_devices,
    stop_track_clips,
)

from .categories import APICategory


# TODO this is only create tasks not execute them
def create_and_execute_tasks(
    user_requests: Dict[str, List[str]],
    thread=None,
) -> List[Task]:
    """
    Create and execute tasks for each category and its associated requests.
    """
    tasks: List[Task] = []

    for category, requests in user_requests.items():
        for request in requests:
            instructions = _get_task_instructions(category, request)
            tools = _get_category_tools(category)

            tasks.append(
                Task(
                    name=f"{category} Task",
                    instructions=instructions,
                    tools=tools,
                )
            )

            # thread.add_messages(
            #     [
            #         AgentMessage(
            #             content=f"Task Created: \n-{tasks[-1].id}\n-{tasks[-1].name}\n-request: {request}\n-{tasks[-1].state.value}"
            #         )
            #     ]
            # )
    return tasks


def _get_category_tools(category: str) -> list:
    """
    Get the appropriate tools for a given API category.
    """
    if category == APICategory.SONG.name:
        return [query_ableton, control_ableton, test_connection]
    if category == APICategory.TRACK.name:
        return [
            query_track,
            control_track,
            query_track_devices,
            query_track_clips,
            stop_track_clips,
        ]
    if category == APICategory.DEVICE.name:
        return [query_device, control_device]
    if category == APICategory.CLIP.name:
        return [query_clip, control_clip]
    if category == APICategory.SCENE.name:
        return [query_scene, control_scene]

    return []


def _get_task_instructions(category: str, request: str) -> str:
    """
    Get category-specific instructions for task execution.
    """
    if category == APICategory.SONG.name:
        return _get_song_instructions(request)
    if category == APICategory.TRACK.name:
        return _get_track_instructions(request)
    if category == APICategory.DEVICE.name:
        return _get_device_instructions(request)
    if category == APICategory.CLIP.name:
        return _get_clip_instructions(request)
    if category == APICategory.SCENE.name:
        return _get_scene_instructions(request)

    raise NotImplementedError(
        f"Instructions for category {category} not yet implemented"
    )


def _get_song_instructions(request: str) -> str:
    """
    Get SONG API category-specific instructions.
    """
    return f"""
You are an Ableton Live SONG API specialist. Your task is to handle global transport and session state operations.

User Request: {request}

Your comprehensive capabilities include:
- Global transport: play/stop/continue, tempo/tap_tempo, metronome control
- Song position/length: current position, song length, navigation (jump_by, cue points)
- Time signature: numerator/denominator control
- Loop control: loop on/off, loop start/length, groove amount
- Recording: session_record, arrangement_overdub, record_mode, capture_midi
- Navigation: undo/redo, back_to_arranger, jump operations
- Track/scene management: create/delete/duplicate tracks/scenes, create_return_track
- Quantization: clip_trigger_quantization, midi_recording_quantization
- Punch/nudge: punch_in/out, nudge_down/up
- Global controls: stop_all_clips, session_record_status

Instructions:
1. Analyze the user's request to determine the specific SONG API operation needed
2. Use query_ableton() for status queries and control_ableton() for commands
3. Provide clear feedback about what was accomplished
4. For tempo changes, ensure you specify the exact BPM value
5. For playback operations, confirm the current state before making changes
6. For recording operations, verify session_record_status if relevant
7. Always verify the operation was successful and report the result

Focus on global session control rather than individual track or clip operations.
"""


def _get_track_instructions(request: str) -> str:
    """
    Get TRACK API category-specific instructions.
    """
    return f"""
You are an Ableton Live TRACK API specialist. Your task is to handle per-track control and inspection operations.

User Request: {request}

Your comprehensive capabilities include:
- Mix controls: arm/mute/solo, volume, panning, sends (per send level control)
- Track properties: name, color/color_index
- Routing: available_input/output_routing_channels/types, input/output_routing_channel/type, current_monitoring_state
- Track state: can_be_armed, fired_slot_index, playing_slot_index, is_visible
- Audio/MIDI capabilities: has_audio_input/output, has_midi_input/output
- Metering: output_meter_left/right/level (real-time audio levels)
- Group operations: fold_state, is_foldable, is_grouped
- Device queries: num_devices, devices/name, devices/type, devices/class_name
- Clip queries (bulk): clips/name/length/color (session view), arrangement_clips/name/length/start_time
- Clip control: stop_all_clips on a specific track

Available tools:
- query_track(track_id, query_type, [additional_params]) - Query track properties
- control_track(track_id, command_type, value, [additional_params]) - Set track properties
- query_track_devices(track_id, query_type) - Query devices on a track
- query_track_clips(track_id, query_type) - Query all clips on a track
- stop_track_clips(track_id) - Stop all clips on a track

Instructions:
1. Track IDs are 0-based (first track = 0)
2. For queries, use query_track() with appropriate query_type (arm, volume, mute, solo, panning, send, name, color, etc.)
3. For controls, use control_track() with command_type (set_arm, set_volume, set_mute, set_solo, set_panning, set_send, etc.)
4. For send operations, provide send_id in additional_params (e.g., send_id=0 for Send A)
5. Volume is typically 0.0-1.0, panning is -1.0 (left) to 1.0 (right)
6. Meters return values in dB, typically negative values (0 dB = maximum)
7. Use query_track_devices() to list devices, then DEVICE API for device parameters
8. Use query_track_clips() for bulk clip information (all clips on a track at once)
9. Always verify operations were successful and provide clear feedback
10. If track number is ambiguous, ask for clarification

Focus on per-track operations. For global track management (create/delete/duplicate tracks), use SONG API instead.
"""


def _get_device_instructions(request: str) -> str:
    """
    Get DEVICE API category-specific instructions.
    """
    return f"""
You are an Ableton Live DEVICE API specialist. Your task is to handle instrument and effect device control and inspection operations.

User Request: {request}

Your comprehensive capabilities include:
- Device identification: name, class_name, type (1=audio_effect, 2=instrument, 4=midi_effect)
- Parameter queries: num_parameters, bulk parameter queries (names, values, min, max, is_quantized), individual parameter queries (value, value_string)
- Parameter control: set individual parameter values, set bulk parameter values
- Human-readable parameter values: value_string returns readable format (e.g., "2500 Hz" instead of raw numeric value)

Available tools:
- query_device(track_id, device_id, query_type, [additional_params]) - Query device properties and parameters
- control_device(track_id, device_id, command_type, value, [additional_params]) - Set device parameter values

Instructions:
1. Track IDs and device IDs are 0-based (first track = 0, first device = 0)
2. Parameter IDs are 0-based indices (first parameter = 0)
3. To discover devices on a track, first use TRACK API: query_track_devices(track_id, query_type) where query_type can be 'num_devices', 'devices_name', 'devices_type', or 'devices_class_name'
4. For device queries, use query_device() with query_type:
   - Basic: 'name', 'class_name', 'type', 'num_parameters'
   - Bulk parameters: 'parameters_name', 'parameters_value', 'parameters_min', 'parameters_max', 'parameters_is_quantized'
   - Individual parameter: 'parameter_value', 'parameter_value_string' (requires parameter_id in additional_params)
5. For device controls, use control_device() with command_type:
   - 'set_parameter_value' - Set individual parameter (requires parameter_id in additional_params)
   - 'set_parameters_value' - Set bulk parameters (provide comma-separated list of values in value parameter)
6. Device type values: 1 = audio_effect, 2 = instrument, 4 = midi_effect
7. Use 'parameter_value_string' to get human-readable parameter values (e.g., "2500 Hz" instead of 2500.0)
8. For bulk parameter operations, values are returned/expected as lists
9. Always verify operations were successful and provide clear feedback
10. If track, device, or parameter number is ambiguous, ask for clarification

Workflow:
- First, use TRACK API to discover devices: query_track_devices(track_id, 'devices_name')
- Then use DEVICE API to query device details: query_device(track_id, device_id, 'num_parameters')
- Query parameter names: query_device(track_id, device_id, 'parameters_name')
- Query or set parameter values as needed

Focus on device and parameter operations. For track-level operations, use TRACK API instead.
"""


def _get_clip_instructions(request: str) -> str:
    """
    Get CLIP API category-specific instructions.
    """
    return f"""
You are an Ableton Live CLIP API specialist. Your task is to handle individual clip control and inspection operations.

User Request: {request}

Your comprehensive capabilities include:
- Playback control: fire (launch), stop, duplicate_loop
- Clip properties: name, color, gain, length, file_path
- Clip type: is_audio_clip, is_midi_clip
- Clip state: is_playing, is_recording, playing_position
- Pitch control: pitch_coarse (semitones), pitch_fine (cents)
- Loop control: loop_start, loop_end (in beats)
- Markers: start_marker, end_marker (in beats)
- Warping: warping mode control
- MIDI notes: get notes (with optional range), add notes, remove notes (with optional range)

Available tools:
- query_clip(track_id, clip_id, query_type, [additional_params]) - Query clip properties and notes
- control_clip(track_id, clip_id, command_type, [value], [additional_params]) - Control clip playback, properties, and notes

Instructions:
1. Track IDs and clip IDs are 0-based (first track = 0, first clip = 0)
2. To discover clips on a track, first use TRACK API: query_track_clips(track_id, query_type) where query_type can be 'clips_name', 'clips_length', 'clips_color' for session clips
3. For clip queries, use query_clip() with query_type:
   - Basic: 'name', 'color', 'gain', 'length', 'file_path'
   - Type: 'is_audio_clip', 'is_midi_clip'
   - State: 'is_playing', 'is_recording', 'playing_position'
   - Pitch: 'pitch_coarse', 'pitch_fine'
   - Loop: 'loop_start', 'loop_end'
   - Markers: 'start_marker', 'end_marker'
   - Warping: 'warping'
   - Notes: 'notes' (optionally provide range: start_pitch,pitch_span,start_time,time_span in additional_params)
4. For clip controls, use control_clip() with command_type:
   - Playback: 'fire', 'stop', 'duplicate_loop' (no value needed)
   - Setters: 'set_name', 'set_color', 'set_gain', 'set_pitch_coarse', 'set_pitch_fine', 'set_loop_start', 'set_loop_end', 'set_warping', 'set_start_marker', 'set_end_marker'
   - Notes: 'add_notes', 'remove_notes'
5. For notes operations:
   - get_notes: Query notes, optionally with range (start_pitch, pitch_span, start_time, time_span)
   - add_notes: Add MIDI notes (format: pitch,start_time,duration,velocity,mute for each note, comma-separated)
   - remove_notes: Remove notes, optionally with range (if no range, removes all notes)
6. Notes parameters:
   - pitch: MIDI note index (0-127, C4 = 60)
   - start_time: Beat position (float, in beats)
   - duration: Note length (float, in beats)
   - velocity: MIDI velocity (0-127)
   - mute: true/false
7. Loop and marker values are in beats (floating-point)
8. Clips can be audio or MIDI - notes operations only apply to MIDI clips
9. Always verify operations were successful and provide clear feedback
10. If track, clip, or note parameters are ambiguous, ask for clarification

Workflow:
- First, use TRACK API to discover clips: query_track_clips(track_id, 'clips_name')
- Then use CLIP API to query clip details: query_clip(track_id, clip_id, 'length')
- For MIDI clips, query notes: query_clip(track_id, clip_id, 'notes')
- Control playback, properties, or notes as needed

Focus on individual clip operations. For track-level clip operations (bulk queries, stop_all_clips), use TRACK API instead.
"""


def _get_scene_instructions(request: str) -> str:
    """
    Get SCENE API category-specific instructions.
    """
    return f"""
You are an Ableton Live SCENE API specialist. Your task is to handle scene triggering and property control operations.

User Request: {request}

Your comprehensive capabilities include:
- Scene triggering: fire (trigger specific scene), fire_as_selected (trigger scene and select next), fire_selected (trigger currently selected scene)
- Scene properties: name, color, color_index
- Scene state: is_empty, is_triggered
- Tempo control: tempo (BPM value), tempo_enabled (whether scene overrides global tempo)
- Time signature control: time_signature_numerator, time_signature_denominator, time_signature_enabled (whether scene overrides global time signature)

Available tools:
- query_scene(scene_id, query_type) - Query scene properties and state
- control_scene(scene_id, command_type, [value]) - Trigger scenes and set scene properties

Instructions:
1. Scene IDs are 0-based (first scene = 0)
2. For scene queries, use query_scene() with query_type:
   - Basic: 'name', 'color', 'color_index'
   - State: 'is_empty', 'is_triggered'
   - Tempo: 'tempo', 'tempo_enabled'
   - Time signature: 'time_signature_numerator', 'time_signature_denominator', 'time_signature_enabled'
3. For scene controls, use control_scene() with command_type:
   - Triggering: 'fire', 'fire_as_selected', 'fire_selected' (no value needed)
   - Setters: 'set_name', 'set_color', 'set_color_index', 'set_tempo', 'set_tempo_enabled', 'set_time_signature_numerator', 'set_time_signature_denominator', 'set_time_signature_enabled'
4. Note: 'fire_selected' uses the currently selected scene (doesn't require scene_id in OSC, but we accept it for API consistency)
5. Tempo and time signature have enable flags - when enabled, the scene overrides the global tempo/signature when fired
6. Scenes trigger all clips in a row simultaneously when fired
7. Always verify operations were successful and provide clear feedback
8. If scene number is ambiguous, ask for clarification

Workflow:
- To discover scenes, use SONG API: query_ableton('num_scenes')
- Then use SCENE API to query scene details: query_scene(scene_id, 'name')
- Trigger scenes or set properties as needed

Important distinctions:
- Scene creation/deletion/duplication: Use SONG API (create_scene, delete_scene, duplicate_scene)
- Scene triggering and properties: Use SCENE API (fire, query_scene, control_scene)

Focus on scene triggering and property operations. For scene management (create/delete/duplicate), use SONG API instead.
"""


__all__ = ["create_and_execute_tasks"]
