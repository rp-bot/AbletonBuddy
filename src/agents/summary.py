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


async def generate_conversation_title(thread: marvin.Thread) -> str:
    """
    Generate a concise title for a conversation thread.
    
    Args:
        thread: A Marvin thread object
        
    Returns:
        str: A short, concise title (50-60 characters max) describing the main topic/request
    """
    thread_messages = thread.get_messages()

    instructions = (
        "Generate a short, concise title for this conversation. "
        "The title should capture the main topic or request from the user. "
        "Keep it to 50-60 characters maximum. "
        "Use clear, simple language without technical jargon. "
        "Focus on what the user asked for or what the conversation is about. "
        "Do not include punctuation at the end unless necessary. "
        "Examples: 'Create new track', 'Adjust volume levels', 'Set up MIDI device'"
    )

    title = await marvin.summarize_async(thread_messages, instructions=instructions)
    
    # Ensure title is within character limit
    if len(title) > 60:
        title = title[:57] + "..."
    
    return title.strip()


__all__ = ["summarize_thread", "generate_conversation_title"]

