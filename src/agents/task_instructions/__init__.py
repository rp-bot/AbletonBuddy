"""
Task instruction generators for each API category.
"""

from .application import get_application_instructions
from .clip import get_clip_instructions
from .clip_slot import get_clip_slot_instructions
from .device import get_device_instructions
from .device_loader import get_device_loader_instructions
from .scene import get_scene_instructions
from .song import get_song_instructions
from .track import get_track_instructions
from .view import get_view_instructions
from .composition import get_composition_instructions

__all__ = [
    "get_song_instructions",
    "get_track_instructions",
    "get_device_instructions",
    "get_clip_instructions",
    "get_scene_instructions",
    "get_clip_slot_instructions",
    "get_view_instructions",
    "get_application_instructions",
    "get_composition_instructions",
    "get_device_loader_instructions",
]

