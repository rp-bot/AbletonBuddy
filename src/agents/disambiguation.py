"""
Utilities for clarifying and de-ambiguating user requests.
"""

import marvin


async def remove_ambiguity(
    user_input: str, thread: marvin.Thread | None = None
) -> str:
    """
    Remove ambiguity from user input by resolving pronouns, unclear references, and incomplete commands.
    """
    instructions = (
        "Task: You are an agent that 'cleans' a user's command for the *next* agent in a pipeline. \n"
        "Your *only* job is to identify and resolve ambiguity. You do *not* validate if the command is possible in Ableton. You *only* check if it's *incomplete*.\n\n"
        "Your response must be ONLY the resulting text. Do not add commentary.\n\n"
        "Core Principle: "
        "A command is **ambiguous** *only if* it clearly states an action (like 'set', 'mute', 'create', 'play') but is obviously *missing* a required *target* (like 'track 1', 'the selected clip'), a required *value* (like '120 BPM', '0.8'), or a required *type* (like 'audio track').\n\n"
        "If a command is *not* obviously missing any of these, **you must pass it through as-is**. It is the *next* agent's job to map it to an API call or reject it.\n\n"
        "---------------------------------\n"
        "How to Handle Different Cases:\n"
        "---------------------------------\n\n"
        "Case 1: The command is **Apparently Complete**.\n"
        "-   **Rule:** The command is *not* actively or obviously missing a target, value, or type. This includes simple commands, commands with all parameters, or multi-step commands.\n"
        "-   **Action:** Return the command exactly as-is.\n\n"
        "Case 2: The command is **Truly Ambiguous** (Missing Info).\n"
        "-   **Rule:** The command clearly states an action but is obviously missing its target, its value, or its type.\n"
        "-   **Action:** Return a 'NEED_MORE_CONTEXT:' message asking a *specific* question to get *only* the missing information.\n\n"
        "Case 3: The command uses **Resolvable Targets** (Implicit or Named).\n"
        "-   **Rule:** The command is complete, but uses a *name* (e.g., 'Bass' track) or an *implicit* word (e.g., 'selected', 'current') instead of a specific API index.\n"
        "-   **Action:** Annotate the target with brackets `[]` so the next agent knows to perform a lookup. (e.g., 'mute [track_name='Bass']' or 'arm [selected_track]').\n"
        "---------------------------------\n\n"
        "Input:\n"
        f"{user_input}\n\n"
        "Disambiguated Output:"
    )

    return await marvin.run_async(
        instructions=instructions,
        result_type=str,
        # thread=thread,
    )


def is_ambiguous_input(user_input: str) -> bool:
    """
    Check if the user input is too ambiguous and needs clarification.
    """
    return user_input.startswith("NEED_MORE_CONTEXT:")


def handle_ambiguous_input(user_input: str) -> str:
    """
    Handle ambiguous input by asking the user for clarification.
    """
    if not is_ambiguous_input(user_input):
        return user_input

    parts = user_input.split("Original:")
    if len(parts) > 1:
        clarification_request = parts[0].replace("NEED_MORE_CONTEXT:", "").strip()
        original_input = parts[1].strip()

        return (
            "I need more information to help you. "
            f"{clarification_request}\n\nYour original request: '{original_input}'\n\n"
            "Please provide more specific details and I'll be happy to help!"
        )

    return (
        "I need more information to help you. "
        f"{user_input}\n\nPlease provide more specific details and I'll be happy to help!"
    )


__all__ = ["remove_ambiguity", "is_ambiguous_input", "handle_ambiguous_input"]

