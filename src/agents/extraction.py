"""
Extraction helpers for Ableton agent requests.
"""

from typing import Dict, List, Any

import marvin

from .categories import APICategory


def _flatten_list(items: Any) -> List[str]:
    """
    Flatten a potentially nested list structure into a flat list of strings.
    Handles cases like: ['item'], [['item']], [[['item']]], etc.
    """
    result = []
    if items is None:
        return result

    if isinstance(items, str):
        return [items] if items.strip() else []

    if isinstance(items, list):
        for item in items:
            if isinstance(item, str):
                if item.strip():
                    result.append(item)
            elif isinstance(item, list):
                # Recursively flatten nested lists
                result.extend(_flatten_list(item))
            elif item is not None:
                # Convert other types to string
                str_item = str(item).strip()
                if str_item:
                    result.append(str_item)

    return result


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
        "- Include both ACTION requests (commands to do something) and STATUS requests (queries for information).\n"
        "- Include questions and statements that request information or actions.\n\n"
        "Extraction Guidelines:\n"
        "- Understand the semantic intent of the operations described in the category focus below.\n"
        "- Extract any portion of the user's text that expresses operations matching those semantic concepts.\n"
        "- Extract the complete phrase that expresses the intent, even if it contains multiple words.\n"
        "- For multi-step requests, extract each relevant part separately.\n"
        "- Ignore unrelated filler or commentary that does not change the concrete request.\n"
        "- Prefer the most specific spans that still read as self-contained instructions.\n"
        "- Focus on what the user wants to accomplish, not on specific words or phrases.\n\n"
    )

    specifics = {
        APICategory.APPLICATION.name: (
            "\nAPPLICATION API category\n"
            "Category focus:\n"
            "- Connectivity diagnostics: testing or checking if AbletonOSC is responding or connected.\n"
            "- Application metadata: queries about Ableton Live version information.\n"
            "- Server configuration: getting or setting log levels, reloading/restarting the API server.\n"
            "- These are system-level operations, not musical/creative operations.\n"
            "Extract any requests about connection status, Live version, log levels, or server management."
        ),
        APICategory.SONG.name: (
            "\nSONG API category\n"
            "Category focus:\n"
            "- Global transport: starting/stopping/continuing playback, tempo changes, metronome, song position, time signature.\n"
            "- Loop control: enabling/disabling loops, setting loop boundaries (start, length, bars/beats).\n"
            "- Recording: starting/stopping session or arrangement recording, overdub modes, capturing MIDI.\n"
            "- Navigation: jumping forward/backward, moving to cue points, undo/redo, switching to arrangement view.\n"
            "- Track/scene management: creating, deleting, or duplicating tracks or scenes (global operations).\n"
            "- Quantization: setting quantization for clip triggers or MIDI recording.\n"
            "- Punch/nudge: punch in/out points, nudging song position.\n"
            "- Global controls: stopping all clips, checking recording status.\n"
            "Extract requests about global session state, transport, tempo, loops, recording, or track/scene creation/deletion."
        ),
        APICategory.VIEW.name: (
            "\nVIEW API category\n"
            "Category focus:\n"
            "- Selection queries: asking what track, scene, clip, or device is currently selected/focused in the UI.\n"
            "- Selection control: changing which track, scene, clip, or device is selected/focused.\n"
            "- Listening: starting or stopping monitoring of selection changes.\n"
            "- VIEW is about UI focus and navigation only; actual edits to selected items use other APIs.\n"
            "Extract requests about querying or changing what's selected in the interface, or listening to selection changes."
        ),
        APICategory.TRACK.name: (
            "\nTRACK API category\n"
            "Category focus:\n"
            "- Per-track mix controls: arming, muting, soloing, volume, panning, send levels.\n"
            "- Track properties: name, color, audio meter levels.\n"
            "- Track setup/configuration: setting up, configuring, or preparing a track (naming, coloring, setting initial properties).\n"
            "- Routing: input/output routing channels/types, monitoring state.\n"
            "- Track state queries: checking if track can be armed, which slots are playing, visibility.\n"
            "- Audio/MIDI capabilities: checking what types of input/output a track supports.\n"
            "- Group operations: fold state, grouping status.\n"
            "- Device discovery: listing or querying devices on a track (bulk queries).\n"
            "- Bulk clip queries: getting information about all clips on a track at once.\n"
            "- Clip control: stopping all clips on a specific track.\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to configure, prepare, or set up properties of an existing track.\n"
            "- Operations to control or query mix settings (arm, mute, solo, volume, pan, sends) for a specific track.\n"
            "- Operations to query or modify track properties (name, color, meters, routing, state, capabilities).\n"
            "- Operations to discover or list devices or clips on a track.\n"
            "- Note: Track creation (making new tracks) is SONG API, but track setup/configuration is TRACK API."
        ),
        APICategory.CLIP_SLOT.name: (
            "\nCLIP_SLOT API category\n"
            "Category focus:\n"
            "- Slot actions: firing/playing/pausing a clip slot.\n"
            "- Slot creation/deletion: creating new empty clips in slots (with length specified in bars/beats), deleting clips from slots.\n"
            "- Slot state: checking if a slot has a clip, managing stop buttons.\n"
            "- Slot duplication: copying a clip from one slot to another (can be same or different track).\n"
            "- Slot management operations work on specific track/slot positions, but natural language may omit explicit indices.\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to create new empty clips (the act of bringing a clip into existence, not editing an existing one).\n"
            "- Operations to fire, launch, or play clip slots.\n"
            "- Operations to duplicate clips between slots.\n"
            "- Operations to delete clips from slots or manage slot state.\n"
            "- Important: The intent to create a new clip should be extracted regardless of how it's phrased or whether track/slot numbers are specified."
        ),
        APICategory.CLIP.name: (
            "\nCLIP API category\n"
            "Category focus:\n"
            "- Playback control: launching, stopping, or duplicating loops of a specific clip.\n"
            "- Clip properties: name, color, gain, length, file path.\n"
            "- Clip type: checking if a clip is audio or MIDI.\n"
            "- Clip state: checking if clip is playing, recording, or its current position.\n"
            "- Pitch control: transposing clips (coarse semitones, fine cents).\n"
            "- Loop control: setting loop start and end points (in beats).\n"
            "- Markers: setting start and end markers (in beats).\n"
            "- Warping: enabling/disabling or configuring warping mode.\n"
            "- MIDI notes: querying notes (optionally with pitch/time ranges), adding notes, removing notes (optionally with ranges).\n"
            "- Operations require identifying a specific clip (track and clip indices).\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to edit, query, or control properties of a specific individual clip that already exists.\n"
            "- Operations to modify or inspect clip properties (name, color, gain, length, pitch, loops, markers, warping).\n"
            "- Operations to work with MIDI notes within a clip (adding, removing, querying notes).\n"
            "- Important distinction: Creating new clips is CLIP_SLOT API. Editing existing clips is CLIP API."
        ),
        APICategory.SCENE.name: (
            "\nSCENE API category\n"
            "Category focus:\n"
            "- Scene triggering: firing/launching/triggering scenes (specific scene, selected scene, or scene with selection advance).\n"
            "- Scene properties: name, color.\n"
            "- Scene state: checking if scene is empty or currently triggered.\n"
            "- Tempo control: setting scene tempo (BPM) and enabling tempo override.\n"
            "- Time signature control: setting scene time signature and enabling override.\n"
            "- Scenes trigger all clips in their row simultaneously.\n"
            "- Note: Scene creation/deletion/duplication are SONG API operations, not SCENE API.\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to trigger, fire, or launch scenes.\n"
            "- Operations to set or query scene properties (name, color, tempo, time signature).\n"
            "- Operations to query scene state (empty, triggered).\n"
        ),
        APICategory.DEVICE.name: (
            "\nDEVICE API category\n"
            "Category focus:\n"
            "- Device identification: getting device names, types (audio effect, instrument, MIDI effect), class names.\n"
            "- Parameter queries: listing parameters, getting parameter values (raw or human-readable), parameter ranges (min/max), quantization status.\n"
            "- Parameter control: setting individual or multiple parameter values.\n"
            "- Human-readable values: getting parameter values in readable formats (e.g., frequency in Hz, not raw numbers).\n"
            "- Operations are scoped to a specific device on a specific track.\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to query or control device parameters (getting or setting parameter values).\n"
            "- Operations to get device information (names, types, class names).\n"
            "- Note: Listing devices on a track is TRACK API, but controlling device parameters is DEVICE API."
        ),
        APICategory.COMPOSITION.name: (
            "\nCOMPOSITION API category\n"
            "Category focus:\n"
            "- Melody generation: creating melodic lines with specified scale/key, length, and style.\n"
            "- Chord progression generation: creating harmonically coherent chord progressions with specified parameters.\n"
            "- Drum pattern generation: creating rhythmically interesting drum patterns for various musical styles.\n"
            "- Musical content generation: requests to generate, create, or make musical content (melodies, chords, drums).\n"
            "- Operations involve generating MIDI notes and creating clips with that content.\n"
            "Extract any portion of the user's request that expresses:\n"
            "- Operations to create or generate melodies (e.g., 'create a melody', 'generate a melodic line', 'make a melody').\n"
            "- Operations to create or generate chord progressions (e.g., 'create a chord progression', 'generate chords', 'make a progression').\n"
            "- Operations to create or generate drum patterns (e.g., 'create a drum pattern', 'generate drums', 'make a beat').\n"
            "- Requests that specify musical parameters like scale/key, style, length in bars for content generation.\n"
            "- Include track and slot information when specified (e.g., 'in track 2', 'on track 1 slot 0', 'in [track 2]').\n"
            "- Extract the complete request including location context (e.g., 'create a hiphop melody 4 bars long in track 2' should extract the full phrase).\n"
            "- Important: This is about GENERATING musical content, not just creating empty clips. Creating empty clips is CLIP_SLOT API."
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
        spans = await marvin.extract_async(
            user_input, List[str], instructions=instructions
        )

        # Flatten and filter the results to handle nested lists
        extracted_requests[category] = _flatten_list(spans)

    return extracted_requests


__all__ = ["extract_user_request"]
