"""
Thread summarisation helpers for Ableton agents.
"""

import marvin


async def summarize_thread(thread: marvin.Thread) -> str:
    """
    Summarize the results of a thread using marvin.summarize.
    """
    thread_messages = thread.get_messages()

    instructions = (
        "Create a concise, easy-to-read summary of this Ableton Live session. "
        "Write in first person from the agent's perspective using 'I' statements. "
        "Format the summary with bullet points and end with 'Do you need me to do anything else?'\n\n"
        "Structure:\n"
        "• What the user asked for\n"
        "• What I accomplished\n"
        "• Key results or changes I made\n"
        "• Whether the request was completed successfully\n"
        "• End with: 'Do you need me to do anything else?'\n\n"
        "Use phrases like 'I did this' or 'I accomplished that'. "
        "Keep it brief and use simple, clear language. "
        "Avoid technical jargon and focus on what the user needs to know."
    )

    summary = await marvin.summarize_async(thread_messages, instructions=instructions)
    return summary


__all__ = ["summarize_thread"]

