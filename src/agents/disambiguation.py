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
        "- 'set send' → needs send_id, send value, and track identifier\n"
        "- 'show track meters' → needs track identifier\n"
        "- 'get track devices' → needs track identifier\n"
        "- 'show track clips' → needs track identifier\n"
        "- 'stop clips on track' → needs track identifier\n"
        "- 'set track routing' → needs routing type/channel and track identifier\n"
        "- 'fold track' → needs track identifier (for group tracks)\n"
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

