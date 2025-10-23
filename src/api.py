"""
FastAPI backend for Ableton Buddy.
Provides REST API endpoints for conversation management and real-time streaming.
"""

from typing import List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import marvin
from marvin.engine.llm import UserMessage, AgentMessage
from marvin.database import get_async_session, DBThread, DBMessage
from sqlalchemy import select, func, desc

# Import configuration to ensure database is set up
import config  # noqa: F401

# Import agent functions
from agents import (
    remove_ambiguity,
    is_ambiguous_input,
    handle_ambiguous_input,
    classify_user_input,
    extract_user_request,
    create_and_execute_tasks,
    summarize_thread,
)

# Import message formatting utilities
from utils.message_formatter import (
    filter_messages_for_display,
    get_detailed_messages,
)

app = FastAPI(title="Ableton Buddy API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class MessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class ThreadSummary(BaseModel):
    thread_id: str
    created_at: str
    message_count: int
    summary: str


class ThreadDetail(BaseModel):
    thread_id: str
    created_at: str
    messages: List[MessageResponse]


class DetailedMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    metadata: Dict[str, Any]
    raw_message: Dict[str, Any]


class ThreadDetailFull(BaseModel):
    thread_id: str
    created_at: str
    messages: List[DetailedMessageResponse]


class StreamEvent(BaseModel):
    event: str
    data: str


@app.get("/")
async def root():
    """API health check."""
    return {"status": "ok", "message": "Ableton Buddy API is running"}


@app.get("/threads", response_model=List[ThreadSummary])
async def list_threads():
    """
    List all conversation threads with summaries.

    Returns:
        List of thread summaries with metadata
    """
    try:
        async with get_async_session() as session:
            # Query all threads ordered by creation date (newest first)
            stmt = select(DBThread).order_by(desc(DBThread.created_at))
            result = await session.execute(stmt)
            threads = result.scalars().all()

            thread_summaries = []
            for thread in threads:
                # Count messages for this thread
                message_count_stmt = select(func.count(DBMessage.id)).where(
                    DBMessage.thread_id == thread.id
                )
                message_count_result = await session.execute(message_count_stmt)
                message_count = message_count_result.scalar() or 0

                # Get the first user message for summary
                first_message_stmt = (
                    select(DBMessage)
                    .where(DBMessage.thread_id == thread.id)
                    .order_by(DBMessage.created_at)
                    .limit(1)
                )
                first_message_result = await session.execute(first_message_stmt)
                first_message = first_message_result.scalar_one_or_none()

                # Generate summary from first message or use default
                if first_message:
                    try:
                        # Try to extract content from the serialized message
                        message_data = first_message.message
                        if isinstance(message_data, dict) and "content" in message_data:
                            summary = (
                                message_data["content"][:100] + "..."
                                if len(message_data["content"]) > 100
                                else message_data["content"]
                            )
                        else:
                            summary = f"Thread with {message_count} messages"
                    except Exception:
                        summary = f"Thread with {message_count} messages"
                else:
                    summary = f"Thread with {message_count} messages"

                thread_summaries.append(
                    ThreadSummary(
                        thread_id=thread.id,
                        created_at=thread.created_at.isoformat(),
                        message_count=message_count,
                        summary=summary,
                    )
                )

            return thread_summaries

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads", response_model=Dict[str, str])
async def create_thread():
    """
    Create a new conversation thread.

    Returns:
        Dictionary with new thread_id
    """
    try:
        thread = marvin.Thread()
        return {
            "thread_id": thread.id,
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/threads/{thread_id}", response_model=ThreadDetail)
async def get_thread(thread_id: str, include_details: bool = False):
    """
    Get a specific thread with all its messages (filtered for display).

    Args:
        thread_id: UUID of the thread
        include_details: If True, includes more detailed agent messages

    Returns:
        Thread details with formatted messages
    """
    try:
        thread = marvin.Thread(id=thread_id)
        messages = thread.get_messages()

        # Filter messages for display (only user and assistant responses)
        filtered_messages = filter_messages_for_display(
            messages, include_details=include_details
        )

        return {
            "thread_id": thread_id,
            "created_at": messages[0].created_at.isoformat()
            if messages
            else datetime.now().isoformat(),
            "messages": filtered_messages,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/threads/{thread_id}/detailed", response_model=ThreadDetailFull)
async def get_thread_detailed(thread_id: str):
    """
    Get a specific thread with all its messages including full details and metadata.

    Args:
        thread_id: UUID of the thread

    Returns:
        Thread details with all messages and metadata
    """
    try:
        thread = marvin.Thread(id=thread_id)
        messages = thread.get_messages()

        # Get all messages with full details
        detailed_messages = get_detailed_messages(messages)

        return {
            "thread_id": thread_id,
            "created_at": messages[0].created_at.isoformat()
            if messages
            else datetime.now().isoformat(),
            "messages": detailed_messages,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads/{thread_id}/messages", response_model=MessageResponse)
async def add_message(thread_id: str, message: MessageRequest):
    """
    Add a message to a thread and get the assistant's response.

    Args:
        thread_id: UUID of the thread
        message: User message content

    Returns:
        Assistant's response message
    """
    try:
        thread = marvin.Thread(id=thread_id)
        user_input = message.content

        # Add user message to thread
        thread.add_messages([UserMessage(content=user_input)])

        # Process through agent pipeline
        disambiguated_input = remove_ambiguity(user_input)
        thread.add_messages(
            [AgentMessage(content=f"Disambiguation Agent: {disambiguated_input}")]
        )

        # Check if still ambiguous
        if is_ambiguous_input(disambiguated_input):
            clarification_message = handle_ambiguous_input(disambiguated_input)
            thread.add_messages([AgentMessage(content=clarification_message)])

            # Return clarification request
            return {
                "id": str(thread.get_messages()[-1].id),
                "role": "assistant",
                "content": clarification_message,
                "timestamp": datetime.now().isoformat(),
            }

        # Classify and extract
        api_categories = classify_user_input(disambiguated_input)
        thread.add_messages(
            [AgentMessage(content=f"Classification Agent: {api_categories}")]
        )

        user_requests = extract_user_request(disambiguated_input, api_categories)
        thread.add_messages(
            [AgentMessage(content=f"Extraction Agent: {user_requests}")]
        )

        # Create and execute tasks
        tasks = create_and_execute_tasks(user_requests, thread)

        for task in tasks:
            task.run()
            if task.is_complete:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Successful:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )
            elif task.is_skipped:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Skipped:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )
            elif task.is_failed:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Failed:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )

        # Summarize results
        summarized_results = summarize_thread(thread)
        thread.add_messages(
            [AgentMessage(content=f"Summarization Agent: {summarized_results}")]
        )

        # Return the summarization as assistant response
        return {
            "id": str(thread.get_messages()[-1].id),
            "role": "assistant",
            "content": summarized_results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads/{thread_id}/stream")
async def stream_message(thread_id: str, message: MessageRequest):
    """
    Add a message to a thread and stream the assistant's response in real-time.

    Uses Server-Sent Events (SSE) to stream progress updates and final response.

    Args:
        thread_id: UUID of the thread
        message: User message content

    Returns:
        SSE stream of events
    """

    async def event_generator():
        try:
            thread = marvin.Thread(id=thread_id)
            user_input = message.content

            # Add user message
            thread.add_messages([UserMessage(content=user_input)])
            yield {"event": "status", "data": "Processing your request..."}

            # Disambiguation
            yield {"event": "status", "data": "Understanding your command..."}
            disambiguated_input = remove_ambiguity(user_input)
            thread.add_messages(
                [AgentMessage(content=f"Disambiguation Agent: {disambiguated_input}")]
            )
            yield {
                "event": "status",
                "data": f"Disambiguated input: {disambiguated_input}",
            }

            # Check if ambiguous
            if is_ambiguous_input(disambiguated_input):
                clarification_message = handle_ambiguous_input(disambiguated_input)
                thread.add_messages([AgentMessage(content=clarification_message)])

                yield {"event": "message", "data": clarification_message}
                yield {"event": "done", "data": "Need clarification"}
                return
            else:
                yield {"event": "status", "data": "Input is not ambiguous"}

            # Classification
            yield {"event": "status", "data": "Identifying operations..."}
            api_categories = classify_user_input(disambiguated_input)
            thread.add_messages(
                [AgentMessage(content=f"Classification Agent: {api_categories}")]
            )
            yield {"event": "status", "data": f"Classification: {api_categories}"}
            # Extraction
            user_requests = extract_user_request(disambiguated_input, api_categories)
            thread.add_messages(
                [AgentMessage(content=f"Extraction Agent: {user_requests}")]
            )
            yield {"event": "status", "data": f"Extraction: {user_requests}"}
            # Task creation
            yield {"event": "status", "data": "Creating tasks..."}
            tasks = create_and_execute_tasks(user_requests, thread)
            # Execute tasks
            yield {"event": "status", "data": f"Executing {len(tasks)} task(s)..."}

            for i, task in enumerate(tasks, 1):
                yield {
                    "event": "status",
                    "data": f"Running task {i}/{len(tasks)}: {task.name} {task.tools}",
                }

                task.run()

                if task.is_complete:
                    thread.add_messages(
                        [
                            AgentMessage(
                                content=f"Task Successful:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                            )
                        ]
                    )
                    yield {
                        "event": "status",
                        "data": f"Task Successful: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
                elif task.is_skipped:
                    thread.add_messages(
                        [
                            AgentMessage(
                                content=f"Task Skipped:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                            )
                        ]
                    )
                    yield {
                        "event": "status",
                        "data": f"Task Skipped: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
                elif task.is_failed:
                    thread.add_messages(
                        [
                            AgentMessage(
                                content=f"Task Failed:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task}\n-{task.state.value}"
                            )
                        ]
                    )
                    yield {
                        "event": "status",
                        "data": f"Task Failed: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
            # Summarize
            yield {"event": "status", "data": "Preparing response..."}
            summarized_results = summarize_thread(thread)
            thread.add_messages(
                [AgentMessage(content=f"Summarization Agent: {summarized_results}")]
            )

            # Send final message
            yield {"event": "message", "data": summarized_results}

            yield {"event": "done", "data": "Complete"}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
