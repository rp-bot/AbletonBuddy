"""
Task orchestration utilities for Ableton agents.
"""

from typing import Dict, List

from marvin import Task

from tools.osc.clip_tools import control_clip, query_clip
from tools.osc.device_tools import control_device, query_device
from tools.osc.device_loader_tools import (
    load_device,
    search_device,
    rebuild_device_cache,
    get_device_cache_size,
    test_load_device,
)
from tools.osc.scene_tools import control_scene, query_scene
from tools.osc.clip_slot_tools import query_clip_slot, control_clip_slot
from tools.osc.song_tools import control_ableton, query_ableton, test_connection
from tools.osc.track_tools import (
    control_track,
    query_track,
    query_track_clips,
    query_track_devices,
    stop_track_clips,
)
from tools.osc.view_tools import control_view, query_view, select_track
from tools.osc.application_tools import query_application, control_application
from tools.osc.composition_tools import (
    create_melody_clip,
    create_chord_progression_clip,
    create_drum_pattern_clip,
)

from .categories import APICategory
from .task_instructions import (
    get_application_instructions,
    get_clip_instructions,
    get_clip_slot_instructions,
    get_device_instructions,
    get_device_loader_instructions,
    get_scene_instructions,
    get_song_instructions,
    get_track_instructions,
    get_view_instructions,
    get_composition_instructions,
)


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
            tools = get_category_tools(category)

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


def _get_task_instructions(category: str, request: str) -> str:
    """
    Get category-specific instructions for task execution.
    """
    if category == APICategory.SONG.name:
        return get_song_instructions(request)
    if category == APICategory.TRACK.name:
        return get_track_instructions(request)
    if category == APICategory.DEVICE.name:
        return get_device_instructions(request)
    if category == APICategory.CLIP.name:
        return get_clip_instructions(request)
    if category == APICategory.SCENE.name:
        return get_scene_instructions(request)
    if category == APICategory.CLIP_SLOT.name:
        return get_clip_slot_instructions(request)
    if category == APICategory.VIEW.name:
        return get_view_instructions(request)
    if category == APICategory.APPLICATION.name:
        return get_application_instructions(request)
    if category == APICategory.COMPOSITION.name:
        return get_composition_instructions(request)
    if category == APICategory.DEVICE_LOADER.name:
        return get_device_loader_instructions(request)

    raise NotImplementedError(
        f"Instructions for category {category} not yet implemented"
    )


def get_category_tools(category: str) -> list:
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
    if category == APICategory.CLIP_SLOT.name:
        return [query_clip_slot, control_clip_slot]
    if category == APICategory.VIEW.name:
        return [query_view, control_view, select_track]
    if category == APICategory.APPLICATION.name:
        return [query_application, control_application]
    if category == APICategory.COMPOSITION.name:
        return [
            create_melody_clip,
            create_chord_progression_clip,
            create_drum_pattern_clip,
            # Include SONG API tools for track creation and queries
            query_ableton,
            control_ableton,
        ]
    if category == APICategory.DEVICE_LOADER.name:
        return [
            load_device,
            search_device,
            rebuild_device_cache,
            get_device_cache_size,
            test_load_device,
            query_view,
            control_view,
            select_track,
        ]

    return []


__all__ = ["create_and_execute_tasks"]
