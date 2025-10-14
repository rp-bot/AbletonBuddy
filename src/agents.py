"""
Marvin agent definitions for the Ableton Pal system.
"""
import marvin
from typing import List, Tuple
from enum import Enum

# Import tools for future use
from tools.osc.song_tools import query_ableton, control_ableton, test_connection


class APICategory(Enum):
    """API categories for classifying user input."""
    APPLICATION = "Application API - Control and query application-level state: startup/errors, logging, and Live version information."
    SONG = "Song API - Top-level song control and global session state: play/stop, tempo, metronome, scenes, tracks, cue points, song position and bulk track/clip data queries."
    VIEW = "View API - User interface and selection control: selected track/scene/clip/device and view-related events."
    TRACK = "Track API - Per-track control and inspection: volume, panning, sends, mute/solo/arm, device lists, meters and clip lists."
    CLIP_SLOT = "Clip Slot API - Clip container operations: create/delete clips, query whether a slot has a clip and manage clip slot state."
    CLIP = "Clip API - Individual clip control: clip playback, looping, notes, length, start time and clip-specific properties."
    SCENE = "Scene API - Scene-level actions: create/duplicate/delete scenes, trigger scenes and query scene indices and properties."
    DEVICE = "Device API - Instrument and effect control: device lists, device parameters, types and per-device property queries."


def classify_user_input(user_input: str) -> List[APICategory]:
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
        "- SONG: Global transport and session state (play/stop, tempo, metronome, scenes list, cue points, song position, bulk track/clip queries).\n"
        "- VIEW: UI selection and view state (selected track/scene/clip/device, navigating/selecting in UI).\n"
        "- TRACK: Per-track operations (volume, pan, sends, mute/solo/arm, meters, devices on a track, track clip lists).\n"
        "- CLIP_SLOT: Operations on a slot that may or may not contain a clip (create/delete clip in slot, check slot state).\n"
        "- CLIP: Operations on an individual clip (launch/stop, looping, length, start time, notes, properties).\n"
        "- SCENE: Scene-level actions (create/duplicate/delete scenes, trigger scenes, scene indices/properties).\n"
        "- DEVICE: Instrument/effect device control and queries (device lists, parameters, device-specific properties).\n\n"
        "Disambiguation rules:\n"
        "- If the request is about PLAY/STOP/tempo/metronome or overall session state: include SONG.\n"
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
        "- 'Increase reverb dry/wet on return A device' => DEVICE (and TRACK if on a track; SONG if global).\n\n"
        "Only return labels from this set: APPLICATION, SONG, VIEW, TRACK, CLIP_SLOT, CLIP, SCENE, DEVICE.\n"
        "Be inclusive when in doubt; multi-label is allowed.\n"
    )

    classification = marvin.classify(
        user_input,
        labels=label_names,
        multi_label=True,
        instructions=guidance,
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
        "- If nothing clearly applies to this category, return an empty list.\n\n"
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
            "Examples: 'show the last error in the log', 'what Live version is running'."
        ),
        APICategory.SONG.name: (
            "\nSONG API category\n"
            "Category focus:\n"
            "- Global transport/session: play/stop/resume, tempo, metronome, cue points, song position, stop all clips.\n"
            "- Scene/track creation/duplication/deletion when framed as global song ops.\n"
            "- Navigation by beats/bars, tap tempo, undo/redo.\n"
            "Examples: 'start playback', 'set tempo to 123', 'stop all clips'."
        ),
        APICategory.VIEW.name: (
            "\nVIEW API category\n"
            "Category focus:\n"
            "- UI selection/navigation: get/set selected track, scene, clip, device.\n"
            "- Start/stop listening to selected items or change what is selected.\n"
            "Examples: 'select the next scene', 'focus the selected clip'."
        ),
        APICategory.TRACK.name: (
            "\nTRACK API category\n"
            "Category focus:\n"
            "- Per-track mix/control: arm/mute/solo, volume, pan, sends, stop all clips on a track.\n"
            "- Track properties: names, meters, routing, devices on a track, clip lists.\n"
            "Examples: 'mute track 2', 'arm bass track', 'set track 1 pan left'."
        ),
        APICategory.CLIP_SLOT.name: (
            "\nCLIP_SLOT API category\n"
            "Category focus:\n"
            "- Slot container operations: create/delete a clip in a slot, check slot has clip, duplicate to another slot, fire a slot.\n"
            "Examples: 'create a new clip in track 2, slot 1', 'does slot 3 have a clip'."
        ),
        APICategory.CLIP.name: (
            "\nCLIP API category\n"
            "Category focus:\n"
            "- Individual clip control/content: launch/stop, loop start/end, length, start/end markers, notes add/remove/get.\n"
            "- Clip properties: gain, color, name, is playing/recording, warping, playing position.\n"
            "Examples: 'loop this clip from bar 5', 'add notes to the clip'."
        ),
        APICategory.SCENE.name: (
            "\nSCENE API category\n"
            "Category focus:\n"
            "- Scene actions/properties: trigger selected/next/specific scene, create/duplicate/delete scenes.\n"
            "- Scene metadata: name/color, tempo/time signature enable and values.\n"
            "Examples: 'launch scene 3', 'duplicate the current scene'."
        ),
        APICategory.DEVICE.name: (
            "\nDEVICE API category\n"
            "Category focus:\n"
            "- Instrument/effect device control and queries: device lists/types, parameter counts, get/set parameter values, ranges, quantization.\n"
            "- When scoped to a specific track/device chain.\n"
            "Examples: 'increase reverb dry/wet', 'set cutoff to 2 kHz on track 1'."
        ),
    }

    return base + specifics.get(category, "")


def extract_user_request(user_input: str, categories: List[APICategory]) -> List[Tuple[APICategory, str]]:
    """
    For each provided API category, extract the slice of the user's input that
    corresponds to that category using marvin.extract, returning a list of
    (category, exact_user_span) pairs. Empty extractions are omitted.

    Args:
        user_input: The raw user input.
        categories: The categories to attempt extraction for (e.g., from classify_user_input).

    Returns:
        List of (APICategory, str) pairs; only non-empty extractions are included.

    Notes:
        - The extracted string must be an exact substring of the user's input. Do not rewrite or infer.
        - If multiple spans in the input could match a category, return the most salient single span for that category.
        - Overlapping intents across categories are allowed and will yield multiple pairs.

    Examples:
        Input: "change the tempo, and mute track 2"
        Output: [(APICategory.SONG, "change the tempo"), (APICategory.TRACK, "mute track 2")]

        Input: "select the next scene and start playback"
        Output: [(APICategory.VIEW, "select the next scene"), (APICategory.SONG, "start playback")]
    """
    extracted_requests: List[Tuple[APICategory, str]] = []
    for category in categories:
        instructions = _instruction_for_category(category)

        spans = marvin.extract(user_input, str, instructions=instructions)
        extracted_requests.append((category, spans))

    return extracted_requests


def create_orchestrator_agent() -> marvin.Agent:
    """
    Create the orchestrator agent that coordinates user requests and delegates to specialized agents.
    """
    return marvin.Agent(
        name="Orchestrator",
        instructions="""
        You are the Orchestrator agent for Ableton Pal, a system that helps users interact with Ableton Live.
        
        Your role is to:
        1. Understand user requests and determine what they want to do
        2. Coordinate with specialized agents when needed
        3. Provide helpful responses about music production and Ableton Live
        4. Guide users on how to use the system effectively
        
        You can help with:
        - General questions about music production
        - Ableton Live workflow guidance
        - Understanding what the system can do
        - Coordinating with specialized agents for specific tasks
        
        Be friendly, helpful, and knowledgeable about music production and Ableton Live.
        If a user asks about controlling Ableton Live directly, let them know that functionality
        will be available through the Song Agent in future versions.
        """,
        description="Coordinates user requests and delegates to specialized agents for Ableton Live control"
    )


def create_song_agent() -> marvin.Agent:
    """
    Create the song agent that handles Ableton Live control via OSC tools.
    This is a skeleton for future implementation.
    """
    return marvin.Agent(
        name="Song Agent",
        instructions="""
        You are the Song Agent for Ableton Pal, specialized in controlling Ableton Live.
        
        Your role is to:
        1. Execute Ableton Live commands via OSC
        2. Query Ableton Live session information
        3. Help users with specific Ableton Live operations
        4. Provide feedback on Ableton Live state and operations
        
        Available tools:
        - query_ableton: Get information about the current session
        - control_ableton: Execute commands in Ableton Live
        - test_connection: Verify connection to Ableton Live
        
        Always check connection status before attempting operations.
        Provide clear feedback about what operations were performed.
        """,
        description="Handles Ableton Live control via OSC tools",
        tools=[query_ableton, control_ableton, test_connection]
    )


def get_available_agents() -> List[marvin.Agent]:
    """
    Get a list of all available agents in the system.
    """
    return [
        create_orchestrator_agent(),
        create_song_agent()
    ]
