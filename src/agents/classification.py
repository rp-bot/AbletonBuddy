"""
Classification helpers for Ableton agent requests.
"""

from typing import List

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
        "- APPLICATION: AbletonOSC diagnostics and application metadata (connectivity test, Live version, log level management, reload).\n"
        "- SONG: Global transport/session control (play/stop/continue, tempo, metronome, song position/length, time signature, loop, recording, undo/redo, navigation, track/scene creation/deletion, quantization, punch/nudge, stop_all_clips).\n"
        "- VIEW: UI selection/navigation (query or set selected track/scene/clip/device, start/stop listening to selection changes).\n"
        "- TRACK: Per-track operations (arm/mute/solo, volume, panning, sends, routing, meters, properties, device lists, bulk clip queries, stop_all_clips).\n"
        "- CLIP_SLOT: Slot container operations (create/delete clip in slot, fire slot, set/inspect stop button, duplicate slot content).\n"
        "- CLIP: Individual clip operations (launch/stop, looping, length, markers, pitch, notes, properties).\n"
        "- SCENE: Scene-level operations (trigger scenes, set scene tempo/time signature/name/color, check scene state).\n"
        "- DEVICE: Device-level operations (list devices, get/set parameters, query parameter metadata).\n\n"
        "Disambiguation rules:\n"
        "- If the request is about PLAY/STOP/tempo/metronome/loop/recording/navigation/undo/redo or overall session state: include SONG.\n"
        "- If it's about track/scene creation/deletion/duplication: include SONG (prefer SONG over TRACK for global track management).\n"
        "- If it's about UI selection (knowing/setting selected track/scene/clip/device) or listening for selection changes: include VIEW (and also include the target domain when follow-up operations are needed).\n"
        "- If it's about a specific track's mix controls (arm/mute/solo/volume/pan/sends), routing, meters, properties (name/color), stopping clips on a track, or querying ALL clips on a track (bulk clip queries): include TRACK.\n"
        "- If it's about CREATING a new clip (e.g., 'create a clip', 'create a 4-bar clip', 'make a new clip'): include CLIP_SLOT (and TRACK if the request also references track-level context).\n"
        "- If it's about deleting a slot clip, firing a slot, duplicating a slot, or checking slot state (has clip / stop button): include CLIP_SLOT.\n"
        "- If it's about editing/launching a SPECIFIC individual clip's content/loop/notes/properties (requires knowing which clip already exists): include CLIP.\n"
        "- Key distinction: 'create a clip' = CLIP_SLOT, 'edit clip X' or 'launch clip X' = CLIP.\n"
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


__all__ = ["classify_user_input"]
