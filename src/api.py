"""
FastAPI backend for Ableton Buddy.
Provides REST API endpoints for conversation management and real-time streaming.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import marvin
from marvin.engine.llm import UserMessage, AgentMessage

# Import configuration to ensure database is set up
import config

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
    get_conversation_summary,
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
        # Query database for all threads
        # Note: This is a simplified implementation
        # In production, you'd want pagination and proper DB queries

        # For now, return empty list as we need to implement DB query
        # TODO: Implement proper thread listing from database
        return []
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
async def get_thread(thread_id: str):
    """
    Get a specific thread with all its messages (filtered for display).

    Args:
        thread_id: UUID of the thread

    Returns:
        Thread details with formatted messages
    """
    try:
        thread = marvin.Thread(id=thread_id)
        messages = thread.get_messages()

        # Filter messages for display (only user and assistant responses)
        filtered_messages = filter_messages_for_display(messages)

        return {
            "thread_id": thread_id,
            "created_at": messages[0].created_at.isoformat()
            if messages
            else datetime.now().isoformat(),
            "messages": filtered_messages,
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

            # Check if ambiguous
            if is_ambiguous_input(disambiguated_input):
                clarification_message = handle_ambiguous_input(disambiguated_input)
                thread.add_messages([AgentMessage(content=clarification_message)])

                yield {"event": "message", "data": clarification_message}
                yield {"event": "done", "data": "Need clarification"}
                return

            # Classification
            yield {"event": "status", "data": "Identifying operations..."}
            api_categories = classify_user_input(disambiguated_input)
            thread.add_messages(
                [AgentMessage(content=f"Classification Agent: {api_categories}")]
            )

            # Extraction
            user_requests = extract_user_request(disambiguated_input, api_categories)
            thread.add_messages(
                [AgentMessage(content=f"Extraction Agent: {user_requests}")]
            )

            # Task creation
            yield {"event": "status", "data": "Creating tasks..."}
            tasks = create_and_execute_tasks(user_requests, thread)

            # Execute tasks
            yield {"event": "status", "data": f"Executing {len(tasks)} task(s)..."}

            for i, task in enumerate(tasks, 1):
                yield {
                    "event": "status",
                    "data": f"Running task {i}/{len(tasks)}: {task.name}",
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
