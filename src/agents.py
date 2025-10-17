"""
Marvin agent definitions for the Ableton Pal system.
"""

import marvin
from typing import List, Dict
from enum import Enum
from marvin import Task

# Import tools for future use
from tools.osc.song_tools import query_ableton, control_ableton, test_connection


class APICategory(Enum):
    """API categories for classifying user input."""

    APPLICATION = "Application API - Control and query application-level state: startup/errors, logging, and Live version information."
    SONG = "Song API - Global transport and session control: play/stop/continue, tempo/tap_tempo, metronome, song position/length, time signature, loop settings, recording/session_record/arrangement_overdub, undo/redo, navigation/jump, track/scene creation/deletion, groove/quantization, punch/nudge, stop_all_clips."
    VIEW = "View API - User interface and selection control: selected track/scene/clip/device and view-related events."
    TRACK = "Track API - Per-track control and inspection: volume, panning, sends, mute/solo/arm, device lists, meters and clip lists."
    CLIP_SLOT = "Clip Slot API - Clip container operations: create/delete clips, query whether a slot has a clip and manage clip slot state."
    CLIP = "Clip API - Individual clip control: clip playback, looping, notes, length, start time and clip-specific properties."
    SCENE = "Scene API - Scene-level actions: create/duplicate/delete scenes, trigger scenes and query scene indices and properties."
    DEVICE = "Device API - Instrument and effect control: device lists, device parameters, types and per-device property queries."


def classify_user_input(
    user_input: str, thread: marvin.Thread | None = None
) -> List[APICategory]:
    """
    Classify user input into one or more API categories using Marvin's classify function.

    Args:
        user_input: The user's input text to classify

    Returns:
        List[APICategory]: The list of classified API categories (may be multiple)
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
        "- TRACK: Per-track operations (volume, pan, sends, mute/solo/arm, meters, devices on a track, track clip lists).\n"
        "- CLIP_SLOT: Operations on a slot that may or may not contain a clip (create/delete clip in slot, check slot state).\n"
        "- CLIP: Operations on an individual clip (launch/stop, looping, length, start time, notes, properties).\n"
        "- SCENE: Scene-level actions (create/duplicate/delete scenes, trigger scenes, scene indices/properties).\n"
        "- DEVICE: Instrument/effect device control and queries (device lists, parameters, device-specific properties).\n\n"
        "Disambiguation rules:\n"
        "- If the request is about PLAY/STOP/tempo/metronome/loop/recording/navigation/undo/redo or overall session state: include SONG.\n"
        "- If it's about track/scene creation/deletion/duplication: include SONG (prefer SONG over TRACK for global track management).\n"
        "- If it's about UI selection/navigating what is selected: include VIEW (and also the target domain when relevant).\n"
        "- If it's about a specific track's mix/arm/solo/devices: include TRACK (and DEVICE if about device params).\n"
        "- If it's about creating/deleting or checking a slot: include CLIP_SLOT.\n"
        "- If it's about editing/launching a concrete clip's content/loop/notes: include CLIP.\n"
        "- If it's about triggering/managing scenes: include SCENE (and SONG if global transport is implicated).\n"
        "- If it's about devices or their parameters: include DEVICE (and TRACK if scoped to a track).\n"
        "- If it's about the Live application lifecycle, version, or logs: include APPLICATION.\n\n"
        "Edge cases:\n"
        "- 'Launch scene 3' => SCENE (and SONG if transport context is implied).\n"
        "- 'Arm track 1 and set volume to -6 dB' => TRACK.\n"
        "- 'Select the currently playing clip' => VIEW and CLIP.\n"
        "- 'Create a new empty clip in track 2, slot 1' => CLIP_SLOT (and TRACK if relevant).\n"
        # "- 'Create new MIDI track' => SONG (global track management).\n"
        "- 'Increase reverb dry/wet on return A device' => DEVICE (and TRACK if on a track; SONG if global).\n\n"
        "Only return labels from this set: APPLICATION, SONG, VIEW, TRACK, CLIP_SLOT, CLIP, SCENE, DEVICE.\n"
        "Be inclusive when in doubt; multi-label is allowed.\n"
    )

    classification = marvin.classify(
        user_input,
        labels=label_names,
        multi_label=True,
        instructions=guidance,
        thread=thread,
    )

    # Convert the result back to the enum
    return classification


def _instruction_for_category(category: APICategory) -> str:
    """
    Build focused extraction instructions for a given API category.
    The instruction should guide extraction toward the subset of the user's
    input that is relevant to that category.
    """
    base = (
        f"Task: From the user's Ableton Live request, extract the EXACT substring(s) that pertain to {category} API category.\n\n"
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
            "- Per-track mix/control: arm/mute/solo, volume, pan, sends, stop all clips on a track.\n"
            "- Track properties: names, meters, routing, devices on a track, clip lists.\n"
            "Examples: 'mute track 2', 'arm bass track', 'set track 1 pan left', 'show all tracks', 'what tracks are armed', 'show track 1 volume'."
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
            "- Individual clip control/content: launch/stop, loop start/end, length, start/end markers, notes add/remove/get.\n"
            "- Clip properties: gain, color, name, is playing/recording, warping, playing position.\n"
            "Examples: 'loop this clip from bar 5', 'add notes to the clip', 'what clips are playing', 'show clip properties', 'is this clip recording'."
        ),
        APICategory.SCENE.name: (
            "\nSCENE API category\n"
            "Category focus:\n"
            "- Scene actions/properties: trigger selected/next/specific scene, create/duplicate/delete scenes.\n"
            "- Scene metadata: name/color, tempo/time signature enable and values.\n"
            "Examples: 'launch scene 3', 'duplicate the current scene', 'show all scenes', 'what scene is selected', 'list scene names'."
        ),
        APICategory.DEVICE.name: (
            "\nDEVICE API category\n"
            "Category focus:\n"
            "- Instrument/effect device control and queries: device lists/types, parameter counts, get/set parameter values, ranges, quantization.\n"
            "- When scoped to a specific track/device chain.\n"
            "Examples: 'increase reverb dry/wet', 'set cutoff to 2 kHz on track 1', 'show all devices on track 1', 'what effects are loaded', 'list device parameters'."
        ),
    }

    return base + specifics.get(category, "")


def extract_user_request(
    user_input: str, categories: List[APICategory], thread: marvin.Thread | None = None
) -> Dict[APICategory, List[str]]:
    """
    For each provided API category, extract the slices of the user's input that
    correspond to that category using marvin.extract, returning a dictionary mapping
    categories to lists of extracted spans.

    Args:
        user_input: The raw user input.
        categories: The categories to attempt extraction for (e.g., from classify_user_input).

    Returns:
        Dictionary mapping APICategory to list of extracted string spans. Categories with no
        extractions will have empty lists.

    Notes:
        - The extracted strings must be exact substrings of the user's input. Do not rewrite or infer.
        - Multiple spans in the input can match a category and will all be included in the list.
        - Overlapping intents across categories are allowed.

    Examples:
        Input: "change the tempo, and mute track 2"
        Output: {
            APICategory.SONG: ["change the tempo"],
            APICategory.TRACK: ["mute track 2"]
        }

        Input: "select the next scene and start playback"
        Output: {
            APICategory.VIEW: ["select the next scene"],
            APICategory.SONG: ["start playback"]
        }
    """
    extracted_requests: Dict[APICategory, List[str]] = {}

    for category in categories:
        instructions = _instruction_for_category(category)
        spans = marvin.extract(user_input, str, instructions=instructions)
        extracted_requests[category] = spans if isinstance(spans, list) else [spans]

    return extracted_requests


def remove_ambiguity(user_input: str, thread: marvin.Thread | None = None) -> str:
    """
    Remove ambiguity from user input by resolving pronouns, unclear references, and incomplete commands.

    Args:
        user_input: The user's input text that may contain ambiguous references or incomplete commands
        thread: Optional Marvin thread for context

    Returns:
        str: The user input with all ambiguous references resolved, or a message if cannot be disambiguated

    Examples:
        Input: "select track 3, arm it."
        Output: "select track 3, arm track 3."

        Input: "create a clip in track 1, then duplicate it."
        Output: "create a clip in track 1, then duplicate the clip in track 1."

        Input: "change the tempo"
        Output: "NEED_MORE_CONTEXT: Please specify the tempo value (e.g., 'change the tempo to 120 BPM'). Original: change the tempo"

        Input: "solo track"
        Output: "NEED_MORE_CONTEXT: Please specify which track to solo (e.g., 'solo track 1' or 'solo the bass track'). Original: solo track"
    """
    instructions = (
        "Task: Remove ambiguity from the user's input by resolving all pronouns, unclear references, and incomplete commands.\n\n"
        "Rules:\n"
        "- Replace pronouns (it, this, that, them, etc.) with the specific noun they refer to.\n"
        "- Replace vague references with the specific items they refer to.\n"
        "- Detect incomplete commands that are missing required values or parameters.\n"
        "- Maintain the original meaning and intent.\n"
        "- Keep the same tone and style as the original input.\n"
        "- If a reference is unclear, make a reasonable inference based on context.\n"
        "- Preserve all specific details like track numbers, scene numbers, etc.\n\n"
        "Common incomplete commands that need clarification:\n"
        "- 'change the tempo' → needs tempo value (e.g., 'to 120 BPM')\n"
        "- 'solo track' → needs track identifier (e.g., 'track 1' or 'bass track')\n"
        "- 'mute track' → needs track identifier\n"
        "- 'arm track' → needs track identifier\n"
        "- 'set volume' → needs volume value and track identifier\n"
        "- 'set pan' → needs pan value and track identifier\n"
        "- 'create clip' → needs track and slot information\n"
        "- 'launch scene' → needs scene identifier\n"
        "- 'set reverb' → needs reverb value and target device/track\n"
        "- 'add effect' → needs effect name and target track\n"
        "- 'record' → needs clarification (track, clip, etc.)\n"
        "- 'play' → needs clarification (track, clip, scene, etc.)\n"
        "- 'stop' → needs clarification (track, clip, all clips, etc.)\n"
        "- 'create track' → needs track type (e.g., 'create MIDI track' or 'create audio track')\n"
        "- 'delete track' → needs track identifier (e.g., 'delete track 1')\n"
        "- 'duplicate track' → needs track identifier (e.g., 'duplicate track 2')\n\n"
        "If the input cannot be disambiguated due to insufficient context, unclear references, or missing required values, "
        "return a helpful message starting with 'NEED_MORE_CONTEXT: ' followed by specific guidance on what information is needed, then the original input.\n\n"
        "Special handling for track operations:\n"
        "- For track creation/deletion/duplication without specific details, add 'using SONG API' to indicate global track management.\n"
        "- Examples: 'create midi track' → 'create MIDI track using SONG API', 'delete track 1' → 'delete track using SONG API'\n\n"
        "Examples:\n"
        "- 'select track 3, arm it' → 'select track 3, arm track 3'\n"
        "- 'create a clip, then duplicate it' → 'create a clip, then duplicate the clip'\n"
        "- 'mute that track and solo this one' → 'mute track 2 and solo track 1' (if context suggests track numbers)\n"
        "- 'create an audio track' → 'create an audio track using SONG API'\n"
        "- 'delete track 1' → 'delete track 1 using SONG API'\n"
        "Input:\n"
        f"{user_input}\n\n"
        "Return only the disambiguated text or the NEED_MORE_CONTEXT message, no additional commentary."
    )

    return marvin.run(
        instructions=instructions,
        result_type=str,
        thread=thread,
    )


def is_ambiguous_input(user_input: str) -> bool:
    """
    Check if the user input is too ambiguous and needs clarification.

    Args:
        user_input: The user's input text to check

    Returns:
        bool: True if the input is ambiguous and needs clarification, False otherwise
    """
    return user_input.startswith("NEED_MORE_CONTEXT:")


def handle_ambiguous_input(user_input: str) -> str:
    """
    Handle ambiguous input by asking the user for clarification.

    Args:
        user_input: The ambiguous user input that starts with "NEED_MORE_CONTEXT:"

    Returns:
        str: A user-friendly message asking for clarification
    """
    if not is_ambiguous_input(user_input):
        return user_input

    # Extract the clarification request from the NEED_MORE_CONTEXT message
    # The format is: "NEED_MORE_CONTEXT: [clarification request]. Original: [original input]"
    parts = user_input.split("Original:")
    if len(parts) > 1:
        clarification_request = parts[0].replace("NEED_MORE_CONTEXT:", "").strip()
        original_input = parts[1].strip()

        return f"I need more information to help you. {clarification_request}\n\nYour original request: '{original_input}'\n\nPlease provide more specific details and I'll be happy to help!"
    else:
        # Fallback if the format is unexpected
        return f"I need more information to help you. {user_input}\n\nPlease provide more specific details and I'll be happy to help!"


def create_and_execute_tasks(
    user_requests: Dict[APICategory, List[str]],
) -> Dict[str, any]:
    """
    Create and execute tasks for each category and its associated requests.

    Args:
        user_requests: Dictionary mapping APICategory to list of extracted request strings
    """
    tasks = []
    task_results = {
        "successful": [],
        "failed": [],
        "skipped": [],
        "total": 0,
    }
    # Process each category and its associated requests
    for category, requests in user_requests.items():
        for request in requests:
            # Get category-specific instructions
            instructions = _get_task_instructions(category, request)

            tasks.append(
                Task(
                    name=f"{category} Task",
                    instructions=instructions,
                    tools=[query_ableton, control_ableton, test_connection],
                )
            )

    # Execute all tasks
    for task in tasks:
        task.run()
        if task.is_complete:
            task_results["successful"].append(task)
        elif task.is_skipped:
            task_results["skipped"].append(task)
        elif task.is_failed:
            task_results["failed"].append(task)
        task_results["total"] += 1
    return task_results


def _get_task_instructions(category: APICategory, request: str) -> str:
    """
    Get category-specific instructions for task execution.

    Args:
        category: The API category for the task
        request: The user's request string

    Returns:
        str: Category-specific instructions for the task
    """
    if category == APICategory.SONG.name:
        return _get_song_instructions(request)
    else:
        raise NotImplementedError(
            f"Instructions for category {category} not yet implemented"
        )


def _get_song_instructions(request: str) -> str:
    """
    Get SONG API category-specific instructions.

    Args:
        request: The user's request string

    Returns:
        str: SONG-specific instructions for the task
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
