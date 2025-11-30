"""
  AbletonBuddy - An agentic system that completes music production tasks in Ableton given a text prompt. Copyright (C) 2025  Pratham Vadhulas
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
import asyncio
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
    generate_conversation_title,
)

# Import message formatting utilities
from utils.message_formatter import (
    filter_messages_for_display,
    get_detailed_messages,
)

app = FastAPI(title="Ableton Buddy API", version="1.0.0")

# Global dictionary to track active streams for cancellation
active_streams = {}

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
            # Calculate actual message count for this thread
            try:
                marvin_thread = marvin.Thread(id=thread.thread_id)
                messages = marvin_thread.get_messages()
                from src.utils.message_formatter import get_display_message_count

                actual_message_count = get_display_message_count(messages)
            except Exception:
                # Fallback to stored count if calculation fails
                actual_message_count = thread.message_count

            # Prioritize title, then first_message_preview, then fallback to message count
            summary = (
                thread.title
                or thread.first_message_preview
                or f"Thread with {actual_message_count} messages"
            )

            # Truncate summary if too long
            if len(summary) > 100:
                summary = summary[:100] + "..."

            thread_summaries.append(
                ThreadSummary(
                    thread_id=thread.thread_id,
                    created_at=thread.created_at.isoformat(),
                    message_count=actual_message_count,
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




async def process_agent_pipeline(
    thread_id: str, user_input: str, event_queue: asyncio.Queue
):
    """
    Process the agent pipeline in a separate task that can be cancelled.
    Sends events to the queue for the SSE stream.
    """
    try:
        thread = marvin.Thread(id=thread_id)

        # Add user message
        thread.add_messages([UserMessage(content=user_input)])
        await event_queue.put({"event": "status", "data": "Processing your request..."})
        thread.add_messages(
            [AgentMessage(content="Status: Processing your request...")]
        )

        # Disambiguation
        await event_queue.put(
            {"event": "status", "data": "Understanding your command..."}
        )
        thread.add_messages(
            [AgentMessage(content="Status: Understanding your command...")]
        )
        disambiguated_input = await remove_ambiguity(user_input)
        thread.add_messages(
            [AgentMessage(content=f"Disambiguation Agent: {disambiguated_input}")]
        )
        await event_queue.put(
            {
                "event": "disambiguation",
                "data": f"Disambiguated input: {disambiguated_input}",
            }
        )

        # Check if ambiguous
        if is_ambiguous_input(disambiguated_input):
            clarification_message = handle_ambiguous_input(disambiguated_input)
            thread.add_messages([AgentMessage(content=clarification_message)])
            # Calculate message count and update thread metadata
            messages = thread.get_messages()
            from src.utils.message_formatter import get_display_message_count

            message_count = get_display_message_count(messages)
            await update_thread_metadata(
                thread_id,
                message_count=message_count,
                last_message=clarification_message,
            )
            
            # Generate title after first message exchange (message_count == 2)
            if message_count == 2:
                try:
                    generated_title = await generate_conversation_title(thread)
                    await update_thread_metadata(thread_id, title=generated_title)
                    # Send title update event to frontend
                    await event_queue.put({"event": "title", "data": generated_title})
                except Exception:
                    # If title generation fails, continue without title
                    pass
            
            await event_queue.put({"event": "assistant", "data": clarification_message})
            await event_queue.put({"event": "done", "data": "Need clarification"})
            return
        else:
            await event_queue.put({"event": "status", "data": "Input is not ambiguous"})

        # Classification
        await event_queue.put({"event": "status", "data": "Identifying operations..."})
        thread.add_messages([AgentMessage(content="Status: Identifying operations...")])
        api_categories = await classify_user_input(disambiguated_input)
        thread.add_messages(
            [AgentMessage(content=f"Classification Agent: {api_categories}")]
        )
        await event_queue.put(
            {"event": "classification", "data": f"Classification: {api_categories}"}
        )

        # Extraction
        await event_queue.put({"event": "status", "data": "Extracting operations..."})
        thread.add_messages([AgentMessage(content="Status: Extracting operations...")])
        user_requests = await extract_user_request(disambiguated_input, api_categories)
        thread.add_messages(
            [AgentMessage(content=f"Extraction Agent: {user_requests}")]
        )
        await event_queue.put(
            {"event": "extraction", "data": f"Extraction: {user_requests}"}
        )

        # Task creation
        await event_queue.put({"event": "status", "data": "Creating tasks..."})
        thread.add_messages([AgentMessage(content="Status: Creating tasks...")])
        tasks = create_and_execute_tasks(user_requests)

        # Execute tasks
        await event_queue.put(
            {"event": "status", "data": f"Executing {len(tasks)} task(s)..."}
        )
        thread.add_messages(
            [AgentMessage(content=f"Status: Executing {len(tasks)} task(s)...")]
        )

        for i, task in enumerate(tasks, 1):
            await event_queue.put(
                {
                    "event": "status",
                    "data": f"Running task {i}/{len(tasks)}: {task.name} {task.tools}",
                }
            )
            thread.add_messages(
                [
                    AgentMessage(
                        content=f"Status: Running task {i}/{len(tasks)}: {task.name} {task.tools}..."
                    )
                ]
            )
            await task.run_async()

            if task.is_complete:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Successful:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )
                await event_queue.put(
                    {
                        "event": "task_success",
                        "data": f"Task Successful: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
                )
            elif task.is_skipped:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Skipped:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )
                await event_queue.put(
                    {
                        "event": "task_skipped",
                        "data": f"Task Skipped: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
                )
            elif task.is_failed:
                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Task Failed:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                        )
                    ]
                )
                await event_queue.put(
                    {
                        "event": "task_failed",
                        "data": f"Task Failed: {task.name} {task.result} {', '.join([tool.__name__ for tool in task.tools])}",
                    }
                )

        # Summarize
        await event_queue.put({"event": "status", "data": "Preparing response..."})
        thread.add_messages([AgentMessage(content="Status: Preparing response...")])
        summarized_results = await summarize_thread(thread)
        thread.add_messages(
            [AgentMessage(content=f"Summarization Agent: {summarized_results}")]
        )

        # Send final message
        await event_queue.put({"event": "assistant", "data": summarized_results})
        # Calculate message count and update thread metadata
        messages = thread.get_messages()
        from src.utils.message_formatter import get_display_message_count

        message_count = get_display_message_count(messages)
        await update_thread_metadata(
            thread_id, message_count=message_count, last_message=summarized_results
        )
        
        # Generate title after first message exchange (message_count == 2)
        if message_count == 2:
            try:
                generated_title = await generate_conversation_title(thread)
                await update_thread_metadata(thread_id, title=generated_title)
                # Send title update event to frontend
                await event_queue.put({"event": "title", "data": generated_title})
            except Exception:
                # If title generation fails, continue without title
                pass
        
        await event_queue.put({"event": "done", "data": "Complete"})

    except asyncio.CancelledError:
        # Handle cancellation - add assistant message and send proper events
        try:
            thread = marvin.Thread(id=thread_id)
            # Add assistant message for the cancellation
            cancelled_message = "Generation stopped by user"
            thread.add_messages(
                [AgentMessage(content=f"Summarization Agent: {cancelled_message}")]
            )

            # Send assistant message first, then cancelled event
            await event_queue.put({"event": "assistant", "data": cancelled_message})
            await event_queue.put(
                {"event": "cancelled", "data": "Generation stopped by user"}
            )
            await event_queue.put({"event": "done", "data": "Cancelled"})

            # Calculate message count and update thread metadata
            messages = thread.get_messages()
            from src.utils.message_formatter import get_display_message_count

            message_count = get_display_message_count(messages)
            await update_thread_metadata(
                thread_id, message_count=message_count, last_message=cancelled_message
            )
            
            # Generate title after first message exchange (message_count == 2)
            if message_count == 2:
                try:
                    generated_title = await generate_conversation_title(thread)
                    await update_thread_metadata(thread_id, title=generated_title)
                    # Send title update event to frontend
                    await event_queue.put({"event": "title", "data": generated_title})
                except Exception:
                    # If title generation fails, continue without title
                    pass
        except Exception:
            pass  # Thread might not exist or be accessible
        raise  # Re-raise to properly handle cancellation
    except Exception as e:
        await event_queue.put({"event": "error", "data": str(e)})


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
        # Check if thread exists in our tracking table
        if not await thread_exists(thread_id):
            yield {"event": "error", "data": "Thread not found"}
            return

        # Create event queue for communication between processing task and SSE stream
        event_queue = asyncio.Queue()

        # Create and start the processing task
        processing_task = asyncio.create_task(
            process_agent_pipeline(thread_id, message.content, event_queue)
        )

        # Register the task in active streams for cancellation
        active_streams[thread_id] = {"task": processing_task, "queue": event_queue}

        try:
            # Stream events from the queue until processing is complete
            while True:
                try:
                    # Wait for next event with timeout to allow checking if task is done
                    event = await asyncio.wait_for(event_queue.get(), timeout=1.0)
                    yield event

                    # Check if this is the final event
                    if event.get("event") in ["done", "cancelled", "error"]:
                        break

                except asyncio.TimeoutError:
                    # Check if processing task is done
                    if processing_task.done():
                        break
                    continue

        except Exception as e:
            yield {"event": "error", "data": str(e)}
        finally:
            # Clean up the active stream
            if thread_id in active_streams:
                del active_streams[thread_id]

            # Cancel the processing task if it's still running
            if not processing_task.done():
                processing_task.cancel()
                try:
                    await processing_task
                except asyncio.CancelledError:
                    pass

    return EventSourceResponse(event_generator())


@app.delete("/threads/{thread_id}/stream")
async def cancel_stream(thread_id: str):
    """
    Cancel an active stream for the given thread.

    Args:
        thread_id: UUID of the thread to cancel

    Returns:
        Success message
    """
    try:
        if thread_id not in active_streams:
            raise HTTPException(
                status_code=404, detail="No active stream found for this thread"
            )

        stream_info = active_streams[thread_id]
        task = stream_info["task"]

        # Cancel the processing task immediately
        task.cancel()

        # Clean up the active stream
        del active_streams[thread_id]

        return {"message": f"Stream for thread {thread_id} cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
