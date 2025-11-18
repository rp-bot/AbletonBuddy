"""
Core API category definitions used across Ableton agents.
"""

from enum import Enum


class APICategory(Enum):
    """API categories for classifying user input."""

    APPLICATION = (
        "Application API - Control and query application-level state: startup/errors, "
        "logging, and Live version information."
    )
    SONG = (
        "Song API - Global transport and session control: play/stop/continue, tempo/"
        "tap_tempo, metronome, song position/length, time signature, loop settings, "
        "recording/session_record/arrangement_overdub, undo/redo, navigation/jump, "
        "track/scene creation/deletion, groove/quantization, punch/nudge, stop_all_clips."
    )
    VIEW = (
        "View API - User interface and selection control: selected track/scene/clip/"
        "device and view-related events."
    )
    TRACK = (
        "Track API - Per-track control and inspection: volume, panning, sends, mute/solo/"
        "arm, device lists, meters and clip lists."
    )
    CLIP_SLOT = (
        "Clip Slot API - Clip container operations: create/delete empty clips, query whether "
        "a slot has a clip and manage clip slot state. Note: For creating clips with musical "
        "content (melodies, chords, drums), use COMPOSITION API instead."
    )
    CLIP = (
        "Clip API - Individual clip control: clip playback, looping, notes, length, "
        "start time and clip-specific properties."
    )
    SCENE = (
        "Scene API - Scene-level actions: create/duplicate/delete scenes, trigger scenes "
        "and query scene indices and properties."
    )
    DEVICE = (
        "Device API - Instrument and effect control: device lists, device parameters, "
        "types and per-device property queries."
    )
    DEVICE_LOADER = (
        "Device Loader API - Browser-powered search and loading of instruments/effects/"
        "sounds onto the selected track, plus cache management (search, load, rebuild "
        "cache, cache size, test load). Often combined with VIEW to pick the target track."
    )
    COMPOSITION = (
        "Composition API - MIDI content generation: creating musically coherent melodies, "
        "chord progressions, and drum patterns in MIDI clips."
    )


__all__ = ["APICategory"]
