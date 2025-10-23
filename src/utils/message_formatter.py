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
                    # Handle case where content is a list
                    if isinstance(part.content, list):
                        for item in part.content:
                            if isinstance(item, str):
                                content += item + " "
                            else:
                                content += str(item) + " "
                    # Handle case where content is a string
                    elif isinstance(part.content, str):
                        content += part.content + " "
                    else:
                        content += str(part.content) + " "
        # Try direct content attribute
        elif hasattr(msg_obj, "content"):
            if isinstance(msg_obj.content, list):
                for item in msg_obj.content:
                    if isinstance(item, str):
                        content += item + " "
                    else:
                        content += str(item) + " "
            else:
                content = str(msg_obj.content)
    elif hasattr(message, "content"):
        if isinstance(message.content, list):
            for item in message.content:
                if isinstance(item, str):
                    content += item + " "
                else:
                    content += str(item) + " "
        else:
            content = str(message.content)

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

        # Only UserMessage is definitely a user message
        if message_type == "UserMessage":
            return True

        # For ModelRequest, check the content to determine if it's actually a user message
        if message_type == "ModelRequest":
            content = extract_message_content(message)
            # If it starts with task tags or contains agent keywords, it's not a user message
            if (
                content.startswith("<task>")
                or content.startswith("Summarization Agent:")
                or content.startswith("Disambiguation Agent:")
                or content.startswith("Classification Agent:")
                or content.startswith("Extraction Agent:")
                or content.startswith("Task Created:")
                or content.startswith("Task Successful:")
                or content.startswith("Task Failed:")
                or content.startswith("Task Skipped:")
            ):
                return False
            # Otherwise, it's likely a user message
            return True

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
    return (
        content.startswith("Summarization Agent:")
        or content.startswith("<task>")
        or "Summarize Task" in content
    )


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


def filter_messages_for_display(
    messages: List, include_details: bool = False
) -> List[Dict[str, Any]]:
    """
    Filter thread messages to show user-facing content with optional details.

    Args:
        messages: List of Marvin message objects
        include_details: If True, includes more detailed agent messages

    Returns:
        List[dict]: Filtered and formatted messages
    """
    filtered = []

    for message in messages:
        # Always keep user messages
        if is_user_message(message):
            filtered.append(format_message_for_display(message))
        # Keep summarization messages (assistant responses)
        elif is_summarization_message(message):
            filtered.append(format_message_for_display(message))
        # Optionally include detailed agent messages
        elif include_details:
            content = extract_message_content(message)
            # Include task results and important agent messages
            if any(
                keyword in content
                for keyword in [
                    "Task Successful",
                    "Task Failed",
                    "Task Skipped",
                    "Disambiguation Agent",
                    "Classification Agent",
                    "Extraction Agent",
                ]
            ):
                formatted = format_message_for_display(message)
                formatted["role"] = "system"  # Mark as system message
                filtered.append(formatted)

    return filtered


def get_detailed_messages(messages: List) -> List[Dict[str, Any]]:
    """
    Get all messages with full details preserved.

    Args:
        messages: List of Marvin message objects

    Returns:
        List[dict]: All messages with full details
    """
    detailed = []

    for message in messages:
        content = extract_message_content(message)

        # Determine role based on message type
        if is_user_message(message):
            role = "user"
        elif is_summarization_message(message):
            role = "assistant"
        elif "Disambiguation Agent" in content:
            role = "disambiguation"
        elif "Classification Agent" in content:
            role = "classification"
        elif "Extraction Agent" in content:
            role = "extraction"
        elif "Task Created" in content:
            role = "task_created"
        elif "Task Successful" in content:
            role = "task_success"
        elif "Task Failed" in content:
            role = "task_failed"
        elif "Task Skipped" in content:
            role = "task_skipped"
        else:
            role = "system"

        # Extract additional metadata
        metadata = {}
        if hasattr(message, "message") and hasattr(message.message, "usage"):
            metadata["usage"] = (
                message.message.usage.__dict__
                if hasattr(message.message.usage, "__dict__")
                else {}
            )

        if hasattr(message, "message") and hasattr(message.message, "timestamp"):
            metadata["message_timestamp"] = (
                message.message.timestamp.isoformat()
                if hasattr(message.message.timestamp, "isoformat")
                else str(message.message.timestamp)
            )

        detailed.append(
            {
                "id": str(message.id) if hasattr(message, "id") else None,
                "role": role,
                "content": content,
                "timestamp": message.created_at.isoformat()
                if hasattr(message, "created_at")
                else None,
                "metadata": metadata,
                "raw_message": {
                    "type": type(message.message).__name__
                    if hasattr(message, "message")
                    else None,
                    "parts_count": len(message.message.parts)
                    if hasattr(message, "message") and hasattr(message.message, "parts")
                    else 0,
                },
            }
        )

    return detailed


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
