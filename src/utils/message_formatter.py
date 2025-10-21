"""
Message formatting utilities for Ableton Buddy.
Filters and formats thread messages for clean display.
"""

from typing import List, Dict, Any
from datetime import datetime


def extract_message_content(message) -> str:
    """
    Extract content from a Marvin message object.

    Args:
        message: A Marvin message object

    Returns:
        str: The extracted content text
    """
    content = ""

    # Handle different message structures
    if hasattr(message, "message"):
        msg_obj = message.message

        # Try to extract from parts
        if hasattr(msg_obj, "parts"):
            for part in msg_obj.parts:
                if hasattr(part, "content"):
                    content += part.content + " "
        # Try direct content attribute
        elif hasattr(msg_obj, "content"):
            content = msg_obj.content
    elif hasattr(message, "content"):
        content = message.content

    return content.strip()


def is_user_message(message) -> bool:
    """
    Check if a message is from the user.

    Args:
        message: A Marvin message object

    Returns:
        bool: True if message is from user
    """
    if hasattr(message, "message"):
        message_type = type(message.message).__name__
        return message_type in ["UserMessage", "ModelRequest"]
    return False


def is_summarization_message(message) -> bool:
    """
    Check if a message is a summarization agent message.

    Args:
        message: A Marvin message object

    Returns:
        bool: True if message is a summarization
    """
    content = extract_message_content(message)
    return content.startswith("Summarization Agent:")


def format_message_for_display(message) -> Dict[str, Any]:
    """
    Format a single message for display.

    Args:
        message: A Marvin message object

    Returns:
        dict: Formatted message with role, content, and timestamp
    """
    content = extract_message_content(message)

    # Determine role
    if is_user_message(message):
        role = "user"
    elif is_summarization_message(message):
        role = "assistant"
        # Remove "Summarization Agent:" prefix
        content = content.replace("Summarization Agent:", "").strip()
    else:
        role = "system"

    # Format timestamp
    timestamp = message.created_at if hasattr(message, "created_at") else datetime.now()

    return {
        "id": str(message.id) if hasattr(message, "id") else None,
        "role": role,
        "content": content,
        "timestamp": timestamp.isoformat()
        if isinstance(timestamp, datetime)
        else str(timestamp),
    }


def filter_messages_for_display(messages: List) -> List[Dict[str, Any]]:
    """
    Filter thread messages to show only user-facing content.

    Keeps:
    - User messages
    - Summarization Agent responses (final responses)

    Filters out:
    - Disambiguation Agent messages
    - Classification Agent messages
    - Extraction Agent messages
    - Task Created/Successful/Failed messages
    - Other internal agent messages

    Args:
        messages: List of Marvin message objects

    Returns:
        List[dict]: Filtered and formatted messages
    """
    filtered = []

    for message in messages:
        # Keep user messages
        if is_user_message(message):
            filtered.append(format_message_for_display(message))
        # Keep summarization messages (assistant responses)
        elif is_summarization_message(message):
            filtered.append(format_message_for_display(message))
        # Filter out everything else (internal agent messages)

    return filtered


def format_message_for_cli(message_dict: Dict[str, Any]) -> str:
    """
    Format a message dictionary for CLI display.

    Args:
        message_dict: Formatted message dictionary

    Returns:
        str: CLI-formatted message string
    """
    role = message_dict["role"]
    content = message_dict["content"]

    if role == "user":
        return f"\n🎹 You: {content}"
    elif role == "assistant":
        return f"\n🎵 Assistant: {content}"
    else:
        return f"\n⚙️  System: {content}"


def get_conversation_summary(messages: List) -> str:
    """
    Get a brief summary of a conversation from its messages.

    Args:
        messages: List of Marvin message objects

    Returns:
        str: Brief summary of the conversation
    """
    filtered = filter_messages_for_display(messages)

    if not filtered:
        return "Empty conversation"

    # Get first user message as summary
    for msg in filtered:
        if msg["role"] == "user":
            content = msg["content"]
            # Truncate if too long
            if len(content) > 60:
                content = content[:57] + "..."
            return content

    return "Conversation"
