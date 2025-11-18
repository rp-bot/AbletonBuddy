"""
Utilities for clarifying and de-ambiguating user requests.
"""

import marvin


async def remove_ambiguity(user_input: str, thread: marvin.Thread | None = None) -> str:
    """
    Remove ambiguity from user input by resolving pronouns, unclear references, and incomplete commands.
    """
    instructions = (
        "Task: You are an agent that 'cleans' a user's command for the *next* agent in a pipeline. \n"
        "Your *only* job is to identify and resolve ambiguity, including *pronouns and unclear references*. You do *not* validate if the command is possible in Ableton. You *only* check if it's *incomplete* or *unresolved*.\n\n"
        "Your response must be ONLY the resulting text. Do not add commentary.\n\n"
        "Core Principle: "
        "A command is **ambiguous** *only if* it clearly states an action (like 'set', 'mute') but is obviously *missing* a required *target* ('track 1'), *value* ('120 BPM'), or *type* ('audio track'), OR if it contains a pronoun (like 'it') without a clear reference in the command itself.\n\n"
        "If a command is *not* obviously missing any of these, **you must pass it through as-is** or in its *resolved* form. It is the *next* agent's job to map it to an API call or reject it.\n\n"
        "---------------------------------\n"
        "How to Handle Different Cases:\n"
        "---------------------------------\n\n"
        "Case 1: The command is **Apparently Complete**.\n"
        "-   **Rule:** The command is *not* actively or obviously missing a target, value, or type, and contains no resolvable references.\n"
        "-   **Action:** Return the command exactly as-is.\n\n"
        "Case 2: The command is **Truly Ambiguous** (Missing Info).\n"
        "-   **Rule:** The command clearly states an action but is obviously missing its target, its value, or its type. This *also* includes commands that *only* contain a pronoun (e.g., 'duplicate it'), as the reference is missing.\n"
        "-   **Action:** Return a 'NEED_MORE_CONTEXT:' message asking a *specific* question to get *only* the missing information.\n\n"
        "Case 3: The command uses **Resolvable References**.\n"
        "-   **Rule:** The command is complete, but uses a reference that can be resolved based on context. This includes three types:\n"
        "    1.  **Pronouns:** Words like 'it', 'them', 'this', 'one', where the reference is clear from the *same* command (e.g., 'create a track and name it...').\n"
        "    2.  **Implicit Targets:** Words like 'selected', 'current', 'active'.\n"
        "    3.  **Named Targets:** Specific names like 'Bass' track or 'Reverb' device.\n"
        "-   **Action:** Resolve the reference.\n"
        "    -   For **Pronouns**: *Replace the pronoun* with the noun it refers to (e.g., '...name it' becomes '...name the new track').\n"
        "    -   For **Implicit/Named Targets**: *Annotate the target* with brackets `[]` (e.g., 'arm [selected_track]' or 'mute [track_name='Bass']').\n"
        "---------------------------------\n\n"
        "---------------------------------\n"
        "Indexing Rule:\n"
        "---------------------------------\n"
        "- AbletonOSC APIs use 0-based indices (first track/scene/clip/device = 0).\n"
        "- Users usually speak in 1-based terms (\"track 1\", \"scene 2\").\n"
        "- When you see an explicit number after words like track/scene/clip/device/slot, "
        "convert it to 0-based by subtracting 1 and annotate it, e.g. "
        "'track 2' -> '[track_index=1 (user_requested_track=2)]'.\n"
        "- If the user already says \"track 0\" or \"first track\", keep the number they used but still annotate it so the next agent knows it's already 0-based.\n"
        "\n"
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
