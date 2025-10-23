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
from sqlalchemy import delete
from database import (
    register_thread,
    get_tracked_threads,
    update_thread_metadata,
    delete_tracked_thread,
    thread_exists,
)

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


@app.on_event("startup")
async def startup_event():
    """Initialize custom database table on startup."""
    from database import init_custom_db

    await init_custom_db()


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
        # Get threads from our custom tracking table
        tracked_threads = await get_tracked_threads()

        thread_summaries = []
        for thread in tracked_threads:
            # Use first_message_preview as summary, or fallback to message count
            summary = (
                thread.first_message_preview
                or f"Thread with {thread.message_count} messages"
            )

            # Truncate summary if too long
            if len(summary) > 100:
                summary = summary[:100] + "..."

            thread_summaries.append(
                ThreadSummary(
                    thread_id=thread.thread_id,
                    created_at=thread.created_at.isoformat(),
                    message_count=thread.message_count,
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

        # Register the thread in our custom tracking table
        await register_thread(thread.id)

        return {
            "thread_id": thread.id,
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a conversation thread and all its messages.

    Args:
        thread_id: UUID of the thread to delete

    Returns:
        Success message
    """
    try:
        # Check if thread exists in our tracking table
        if not await thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="Thread not found")

        # Check if thread exists in Marvin
        thread = marvin.Thread(id=thread_id)
        thread.get_messages()  # Verify thread exists

        # Delete the thread (this will cascade delete all messages)
        # Note: Marvin doesn't have a direct delete method, so we'll use the database
        async with get_async_session() as session:
            # Delete all messages for this thread
            await session.execute(
                delete(DBMessage).where(DBMessage.thread_id == thread_id)
            )

            # Delete the thread itself
            await session.execute(delete(DBThread).where(DBThread.id == thread_id))
            await session.commit()

        # Remove from our custom tracking table
        await delete_tracked_thread(thread_id)

        return {"message": f"Thread {thread_id} deleted successfully"}
    except HTTPException:
        raise
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
        # Check if thread exists in our tracking table
        if not await thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="Thread not found")

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
    except HTTPException:
        raise
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
        # Check if thread exists in our tracking table
        if not await thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="Thread not found")

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
    except HTTPException:
        raise
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
        # Check if thread exists in our tracking table
        if not await thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="Thread not found")

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

            # Update thread metadata with the clarification
            await update_thread_metadata(thread_id, last_message=clarification_message)

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
        tasks = create_and_execute_tasks(user_requests)

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

        # Update thread metadata with the final response
        await update_thread_metadata(thread_id, last_message=summarized_results)

        # Return the summarization as assistant response
        return {
            "id": str(thread.get_messages()[-1].id),
            "role": "assistant",
            "content": summarized_results,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
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
            # Check if thread exists in our tracking table
            if not await thread_exists(thread_id):
                yield {"event": "error", "data": "Thread not found"}
                return

            thread = marvin.Thread(id=thread_id)
            user_input = message.content

            # Add user message
            thread.add_messages([UserMessage(content=user_input)])
            yield {"event": "status", "data": "Processing your request..."}
            thread.add_messages(
                [AgentMessage(content="Status: Processing your request...")]
            )
            # Disambiguation
            yield {"event": "status", "data": "Understanding your command..."}
            thread.add_messages(
                [AgentMessage(content="Status: Understanding your command...")]
            )
            disambiguated_input = remove_ambiguity(user_input)
            thread.add_messages(
                [AgentMessage(content=f"Disambiguation Agent: {disambiguated_input}")]
            )
            yield {
                "event": "disambiguation",
                "data": f"Disambiguated input: {disambiguated_input}",
            }

            # Check if ambiguous
            if is_ambiguous_input(disambiguated_input):
                clarification_message = handle_ambiguous_input(disambiguated_input)
                thread.add_messages([AgentMessage(content=clarification_message)])

                # Update thread metadata with the clarification
                await update_thread_metadata(
                    thread_id, last_message=clarification_message
                )

                yield {"event": "assistant", "data": clarification_message}
                yield {"event": "done", "data": "Need clarification"}
                return
            else:
                yield {"event": "status", "data": "Input is not ambiguous"}

            # Classification
            yield {"event": "status", "data": "Identifying operations..."}
            thread.add_messages(
                [AgentMessage(content="Status: Identifying operations...")]
            )
            api_categories = classify_user_input(disambiguated_input)
            thread.add_messages(
                [AgentMessage(content=f"Classification Agent: {api_categories}")]
            )
            yield {
                "event": "classification",
                "data": f"Classification: {api_categories}",
            }
            # Extraction
            yield {"event": "status", "data": "Extracting operations..."}
            thread.add_messages(
                [AgentMessage(content="Status: Extracting operations...")]
            )
            user_requests = extract_user_request(disambiguated_input, api_categories)
            thread.add_messages(
                [AgentMessage(content=f"Extraction Agent: {user_requests}")]
            )
            yield {"event": "extraction", "data": f"Extraction: {user_requests}"}
            # Task creation
            yield {"event": "status", "data": "Creating tasks..."}
            thread.add_messages([AgentMessage(content="Status: Creating tasks...")])
            tasks = create_and_execute_tasks(user_requests)
            # Execute tasks
            yield {"event": "status", "data": f"Executing {len(tasks)} task(s)..."}
            thread.add_messages(
                [AgentMessage(content=f"Status: Executing {len(tasks)} task(s)...")]
            )
            for i, task in enumerate(tasks, 1):
                yield {
                    "event": "status",
                    "data": f"Running task {i}/{len(tasks)}: {task.name} {task.tools}",
                }
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Status: Running task {i}/{len(tasks)}: {task.name} {task.tools}..."
                        )
                    ]
                )
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
                        "event": "task_success",
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
                        "event": "task_skipped",
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
                        "event": "task_failed",
                        "data": f"Task Failed: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
            # Summarize
            yield {"event": "status", "data": "Preparing response..."}
            thread.add_messages([AgentMessage(content="Status: Preparing response...")])
            summarized_results = summarize_thread(thread)
            thread.add_messages(
                [AgentMessage(content=f"Summarization Agent: {summarized_results}")]
            )

            # Send final message
            yield {"event": "assistant", "data": summarized_results}

            # Update thread metadata with the final response
            await update_thread_metadata(thread_id, last_message=summarized_results)

            yield {"event": "done", "data": "Complete"}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
