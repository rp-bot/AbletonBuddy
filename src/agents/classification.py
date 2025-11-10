"""
Classification and extraction helpers for Ableton agent requests.
"""

from typing import Dict, List

import marvin

from .categories import APICategory


async def classify_user_input(
    user_input: str, thread: marvin.Thread | None = None
) -> List[str]:
    """
    Classify user input into one or more API categories using Marvin's classify function.

    Args:
        user_input: The user's input text to classify

    Returns:
        List[str]: The list of classified API category names (may be multiple)
    """
    # Use concise label names for better classification stability
    label_names = [category.name for category in APICategory]

    # Provide rich context and disambiguation guidance to the classifier
    guidance = (
        "Task: Given a user's natural language request about Ableton Live, "
        "select ALL applicable API categories that best match the intended operation(s).\n\n"
        "Categories (choose all that apply):\n"
        "- APPLICATION: Control/query Live application itself (startup/errors, logs, Live version).\n"
        "- SONG: Global transport and session state (play/stop/continue, tempo/tap_tempo, metronome, song position/length, time signature, loop settings, recording/session_record/arrangement_overdub, undo/redo, navigation/jump, track/scene creation/deletion, groove/quantization, punch/nudge, stop_all_clips).\n"
        "- VIEW: UI selection and view state (selected track/scene/clip/device, navigating/selecting in UI).\n"
        "- TRACK: Per-track operations (arm/mute/solo, volume, panning, sends, stop_all_clips on track, name, color/color_index, routing channels/types, monitoring state, meters, fold_state for groups, has_audio/midi_input/output, fired/playing_slot_index, track devices/clips queries).\n"
        "- CLIP_SLOT: Operations on a slot that may or may not contain a clip (create/delete clip in slot, check slot state).\n"
        "- CLIP: Operations on an individual clip (launch/stop, looping, length, start time, notes, properties).\n"
        "- SCENE: Scene-level actions (create/duplicate/delete scenes, trigger scenes, scene indices/properties).\n"
        "- DEVICE: Instrument/effect device control and queries (device lists, parameters, device-specific properties).\n\n"
        "Disambiguation rules:\n"
        "- If the request is about PLAY/STOP/tempo/metronome/loop/recording/navigation/undo/redo or overall session state: include SONG.\n"
        "- If it's about track/scene creation/deletion/duplication: include SONG (prefer SONG over TRACK for global track management).\n"
        "- If it's about UI selection/navigating what is selected: include VIEW (and also the target domain when relevant).\n"
        "- If it's about a specific track's mix controls (arm/mute/solo/volume/pan/sends), routing, meters, properties (name/color), stopping clips on a track, or querying ALL clips on a track (bulk clip queries): include TRACK.\n"
        "- If it's about creating/deleting or checking a slot: include CLIP_SLOT.\n"
        "- If it's about editing/launching a SPECIFIC individual clip's content/loop/notes/properties (requires knowing which clip): include CLIP.\n"
        "- If it's about triggering/managing scenes: include SCENE (and SONG if transport context is implicated).\n"
        "- If it's about devices or their parameters: include DEVICE (and TRACK if scoped to a track).\n"
        "- If it's about the Live application lifecycle, version, or logs: include APPLICATION.\n\n"
        "Edge cases:\n"
        "- 'Launch scene 3' => SCENE (and SONG if transport context is implied).\n"
        "- 'Arm track 1 and set volume to -6 dB' => TRACK.\n"
        "- 'Select the currently playing clip' => VIEW and CLIP.\n"
        "- 'Create a new empty clip in track 2, slot 1' => CLIP_SLOT (and TRACK if relevant).\n"
        "- 'Increase reverb dry/wet on return A device' => DEVICE (and TRACK if on a track; SONG if global).\n\n"
        "Only return labels from this set: APPLICATION, SONG, VIEW, TRACK, CLIP_SLOT, CLIP, SCENE, DEVICE.\n"
        "Be inclusive when in doubt; multi-label is allowed.\n"
    )

    classification = await marvin.classify_async(
        user_input,
        labels=label_names,
        multi_label=True,
        instructions=guidance,
        # thread=thread,
    )

    return classification


def _instruction_for_category(category: str | APICategory) -> str:
    """
    Build focused extraction instructions for a given API category.
    The instruction should guide extraction toward the subset of the user's
    input that is relevant to that category.
    """
    category_name = category.name if isinstance(category, APICategory) else category

    base = (
        f"Task: From the user's Ableton Live request, extract the EXACT substring(s) that pertain to {category_name} API category.\n\n"
        "Constraints:\n"
        "- Return exact substrings from the user's text. Do NOT paraphrase or infer.\n"
        "- If nothing clearly applies to this category, return an empty list.\n"
        "- Include both ACTION requests (commands to do something) and STATUS requests (queries for information).\n\n"
        "Disambiguation:\n"
        "- Ignore unrelated filler or commentary that does not change the concrete request.\n"
        "- Prefer the most specific spans that still read as self-contained instructions.\n\n"
    )

    specifics = {
        APICategory.APPLICATION.name: (
            "\nAPPLICATION API category\n"
            "Category focus:\n"
            "- Live application lifecycle and environment (startup, errors, logs).\n"
            "- Application metadata (e.g., Live version).\n"
            "Examples: 'show the last error in the log', 'what Live version is running', 'check if Live is running', 'show application status'."
        ),
        APICategory.SONG.name: (
            "\nSONG API category\n"
            "Category focus:\n"
            "- Global transport: play/stop/continue, tempo/tap_tempo, metronome, song position/length, time signature.\n"
            "- Loop control: loop on/off, loop start/length, groove amount.\n"
            "- Recording: session_record, arrangement_overdub, record_mode, capture_midi.\n"
            "- Navigation: jump_by, jump_to_next/prev_cue, undo/redo, back_to_arranger.\n"
            "- Track/scene management: create/delete/duplicate tracks/scenes, create_return_track.\n"
            "- Quantization: clip_trigger_quantization, midi_recording_quantization.\n"
            "- Punch/nudge: punch_in/out, nudge_down/up.\n"
            "- Global controls: stop_all_clips, session_record_status.\n"
            "Examples: 'start playback', 'set tempo to 123', 'enable loop from bar 4', 'start session recording', 'create new MIDI track', 'set metronome on', 'jump to next cue', 'undo last action', 'stop all clips'."
        ),
        APICategory.VIEW.name: (
            "\nVIEW API category\n"
            "Category focus:\n"
            "- UI selection/navigation: get/set selected track, scene, clip, device.\n"
            "- Start/stop listening to selected items or change what is selected.\n"
            "Examples: 'select the next scene', 'focus the selected clip', 'what's currently selected', 'show selected track'."
        ),
        APICategory.TRACK.name: (
            "\nTRACK API category\n"
            "Category focus:\n"
            "- Per-track mix controls: arm/mute/solo, volume, panning, sends.\n"
            "- Track properties: name, color/color_index, meters (output_meter_left/right/level).\n"
            "- Routing: available and current input/output routing channels/types, monitoring state.\n"
            "- Track state: can_be_armed, fired_slot_index, playing_slot_index, is_visible.\n"
            "- Audio/MIDI capabilities: has_audio_input/output, has_midi_input/output.\n"
            "- Group operations: fold_state, is_foldable, is_grouped.\n"
            "- Device queries on track: num_devices, devices/name, devices/type, devices/class_name.\n"
            "- Bulk clip queries on track: clips/name/length/color (session), arrangement_clips/name/length/start_time (gets ALL clips on track at once).\n"
            "- Clip control on track: stop_all_clips.\n"
            "Examples: 'mute track 2', 'set track 1 volume to -6 dB', 'arm the bass track', 'set track 3 pan left', 'show track 1 devices', 'get all clip names on track 0', 'what clips are on track 1', 'stop all clips on track 2', 'what is track 1 output level', 'set send A on track 2 to 0.5', 'show track routing options'."
        ),
        APICategory.CLIP_SLOT.name: (
            "\nCLIP_SLOT API category\n"
            "Category focus:\n"
            "- Slot container operations: create/delete a clip in a slot, check slot has clip, duplicate to another slot, fire a slot.\n"
            "Examples: 'create a new clip in track 2, slot 1', 'does slot 3 have a clip', 'show all clip slots', 'what clips are in track 1'."
        ),
        APICategory.CLIP.name: (
            "\nCLIP API category\n"
            "Category focus:\n"
            "- Playback control: fire (launch), stop, duplicate_loop.\n"
            "- Clip properties: name, color, gain, length, file_path.\n"
            "- Clip type: is_audio_clip, is_midi_clip.\n"
            "- Clip state: is_playing, is_recording, playing_position.\n"
            "- Pitch control: pitch_coarse (semitones), pitch_fine (cents).\n"
            "- Loop control: loop_start, loop_end (in beats).\n"
            "- Markers: start_marker, end_marker (in beats).\n"
            "- Warping: warping mode control.\n"
            "- MIDI notes: get notes (with optional range: start_pitch, pitch_span, start_time, time_span), add notes (pitch, start_time, duration, velocity, mute), remove notes (with optional range, or all if no range).\n"
            "- Requires knowing the specific clip (track_id AND clip_id).\n"
            "Examples: 'loop clip 0 on track 1 from bar 5', 'add notes to clip 0 on track 0', 'launch clip 0 on track 1', 'show properties of clip 0 on track 0', 'is clip 0 on track 1 recording', 'what notes are in clip 0 on track 0', 'set the gain of clip 0 on track 1 to 0.8', 'transpose clip 0 on track 0 up by 2 semitones', 'set loop start of clip 0 on track 1 to 8 beats', 'remove all C4 notes from clip 0 on track 0'."
        ),
        APICategory.SCENE.name: (
            "\nSCENE API category\n"
            "Category focus:\n"
            "- Scene triggering: fire (trigger specific scene), fire_as_selected (trigger scene and select next), fire_selected (trigger currently selected scene).\n"
            "- Scene properties: name, color, color_index.\n"
            "- Scene state: is_empty, is_triggered.\n"
            "- Tempo control: tempo (BPM value), tempo_enabled (whether scene overrides global tempo).\n"
            "- Time signature control: time_signature_numerator, time_signature_denominator, time_signature_enabled (whether scene overrides global time signature).\n"
            "- Scenes trigger all clips in a row simultaneously when fired.\n"
            "- Note: Scene creation/deletion/duplication are SONG API operations, not SCENE API.\n"
            "Examples: 'launch scene 3', 'fire scene 0', 'trigger the selected scene', 'what is the name of scene 1', 'set scene 2 tempo to 120 BPM', 'enable tempo override for scene 0', 'show all scene properties', 'is scene 1 empty', 'set scene 0 time signature to 7/8'."
        ),
        APICategory.DEVICE.name: (
            "\nDEVICE API category\n"
            "Category focus:\n"
            "- Device identification: name (human-readable), class_name (Live instrument/effect name), type (1=audio_effect, 2=instrument, 4=midi_effect).\n"
            "- Parameter queries: num_parameters, bulk parameter queries (names, values, min, max, is_quantized), individual parameter queries (value, value_string for human-readable format).\n"
            "- Parameter control: set individual parameter values, set bulk parameter values.\n"
            "- Parameter ranges: query min/max values for parameters, check if parameters are quantized.\n"
            "- Human-readable values: parameter_value_string returns readable format (e.g., '2500 Hz' instead of raw numeric).\n"
            "- When scoped to a specific track/device chain (requires track_id and device_id).\n"
            "Examples: 'increase reverb dry/wet', 'set cutoff to 2 kHz on track 1', 'show all devices on track 1', 'what effects are loaded', 'list device parameters', 'what's the current value of the filter cutoff on device 0, track 1', 'set reverb dry/wet to 0.7', 'show parameter ranges for device 0 on track 0'."
        ),
    }

    return base + specifics.get(category_name, "")


async def extract_user_request(
    user_input: str, categories: List[str], thread: marvin.Thread | None = None
) -> Dict[str, List[str]]:
    """
    For each provided API category, extract the slices of the user's input that
    correspond to that category using marvin.extract, returning a dictionary mapping
    categories to lists of extracted spans.
    """
    extracted_requests: Dict[str, List[str]] = {}

    for category in categories:
        instructions = _instruction_for_category(category)
        spans = await marvin.extract_async(user_input, str, instructions=instructions)
        extracted_requests[category] = spans if isinstance(spans, list) else [spans]

    return extracted_requests


__all__ = ["classify_user_input", "extract_user_request", "APICategory"]

