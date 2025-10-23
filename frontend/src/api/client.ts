/**
 * API client for Ableton Buddy backend
 * Handles all HTTP requests to FastAPI server
 */

import type {
    ThreadSummary,
    ThreadDetail,
    MessageRequest,
    MessageResponse,
    CreateThreadResponse,
} from './types';

const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch all conversation threads
 */
export async function fetchThreads (): Promise<ThreadSummary[]>
{
    const response = await fetch(`${ API_BASE_URL }/threads`);
    if (!response.ok)
    {
        throw new Error('Failed to fetch threads');
    }
    return response.json();
}

/**
 * Create a new conversation thread
 */
export async function createThread (): Promise<CreateThreadResponse>
{
    const response = await fetch(`${ API_BASE_URL }/threads`, {
        method: 'POST',
    });
    if (!response.ok)
    {
        throw new Error('Failed to create thread');
    }
    return response.json();
}

/**
 * Fetch a specific thread with all messages
 */
export async function fetchThread (threadId: string): Promise<ThreadDetail>
{
    const response = await fetch(`${ API_BASE_URL }/threads/${ threadId }/detailed`);
    if (!response.ok)
    {
        throw new Error('Failed to fetch thread');
    }
    return response.json();
}

/**
 * Send a message (non-streaming)
 * Note: Prefer using streaming endpoint for better UX
 */
export async function sendMessage (
    threadId: string,
    message: MessageRequest
): Promise<MessageResponse>
{
    const response = await fetch(`${ API_BASE_URL }/threads/${ threadId }/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    });
    if (!response.ok)
    {
        throw new Error('Failed to send message');
    }
    return response.json();
}

/**
 * Delete a thread and all its messages
 */
export async function deleteThread (threadId: string): Promise<{message: string;}>
{
    const response = await fetch(`${ API_BASE_URL }/threads/${ threadId }`, {
        method: 'DELETE',
    });
    if (!response.ok)
    {
        throw new Error('Failed to delete thread');
    }
    return response.json();
}

/**
 * Create EventSource for streaming messages
 * Note: EventSource only supports GET, so we need to use POST with fetch API
 * for the initial request body, but the backend uses SSE for the response
 */
export function createStreamingConnection (
    threadId: string,
    message: MessageRequest
): EventSource
{
    // Use URLSearchParams to pass the message content as a query parameter
    // This is a workaround since EventSource doesn't support POST
    const params = new URLSearchParams({content: message.content});
    const url = `${ API_BASE_URL }/threads/${ threadId }/stream?${ params }`;

    return new EventSource(url);
}

