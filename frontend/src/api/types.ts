/**
 * TypeScript types matching backend Pydantic models from src/api.py
 */

export interface MessageRequest
{
    content: string;
}

export interface MessageResponse
{
    id: string;
    role: string;
    content: string;
    timestamp: string;
}

export interface ThreadSummary
{
    thread_id: string;
    created_at: string;
    message_count: number;
    summary: string;
}

export interface ThreadDetail
{
    thread_id: string;
    created_at: string;
    messages: MessageResponse[];
}

export interface CreateThreadResponse
{
    thread_id: string;
    created_at: string;
}

// SSE Event types
export type SSEEventType = 'status' | 'message' | 'done' | 'error';

export interface SSEEvent
{
    event: SSEEventType;
    data: string;
}

