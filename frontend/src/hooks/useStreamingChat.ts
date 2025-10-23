/**
 * Custom hook for handling SSE streaming chat with Ableton Buddy backend
 * Uses fetch API with ReadableStream to handle POST requests with SSE
 */

import {useState, useCallback, useRef} from 'react';
import type {MessageRequest} from '@/api/types';

interface StreamingCallbacks
{
    onStatus?: (status: string) => void;
    onMessage?: (message: string) => void;
    onDone?: () => void;
    onError?: (error: string) => void;
}

export function useStreamingChat ()
{
    const [isStreaming, setIsStreaming] = useState(false);
    const [currentStatus, setCurrentStatus] = useState<string>('');
    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(
        async (
            threadId: string,
            message: MessageRequest,
            callbacks: StreamingCallbacks
        ) =>
        {
            // Abort any existing stream
            if (abortControllerRef.current)
            {
                abortControllerRef.current.abort();
            }

            const abortController = new AbortController();
            abortControllerRef.current = abortController;

            setIsStreaming(true);
            setCurrentStatus('Connecting...');

            try
            {
                const response = await fetch(
                    `http://localhost:8000/threads/${ threadId }/stream`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Accept: 'text/event-stream',
                        },
                        body: JSON.stringify(message),
                        signal: abortController.signal,
                    }
                );

                if (!response.ok)
                {
                    throw new Error(`HTTP error! status: ${ response.status }`);
                }

                const reader = response.body?.getReader();
                if (!reader)
                {
                    throw new Error('Response body is not readable');
                }

                const decoder = new TextDecoder();
                let buffer = '';
                let currentEvent = 'message'; // Default event type

                while (true)
                {
                    const {done, value} = await reader.read();

                    if (done)
                    {
                        break;
                    }

                    buffer += decoder.decode(value, {stream: true});
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || ''; // Keep incomplete line in buffer

                    for (const line of lines)
                    {
                        if (!line.trim()) continue;

                        // Parse SSE format: "event: type\ndata: content"
                        if (line.startsWith('event:'))
                        {
                            currentEvent = line.substring(6).trim();
                            continue; // Event type is on separate line
                        }

                        if (line.startsWith('data:'))
                        {
                            const data = line.substring(5).trim();

                            // Handle different event types
                            if (currentEvent === 'done')
                            {
                                setCurrentStatus('');
                                setIsStreaming(false);
                                callbacks.onDone?.();
                            } else if (currentEvent === 'error')
                            {
                                setCurrentStatus('');
                                setIsStreaming(false);
                                callbacks.onError?.(data);
                            } else if (currentEvent === 'status')
                            {
                                setCurrentStatus(data);
                                callbacks.onStatus?.(data);
                            } else if (currentEvent === 'message')
                            {
                                callbacks.onMessage?.(data);
                                setCurrentStatus('');
                            }

                            // Reset to default
                            currentEvent = 'message';
                        }
                    }
                }
            } catch (error)
            {
                if (error instanceof Error)
                {
                    if (error.name === 'AbortError')
                    {
                        console.log('Stream aborted');
                    } else
                    {
                        console.error('Streaming error:', error);
                        setCurrentStatus('');
                        setIsStreaming(false);
                        callbacks.onError?.(error.message);
                    }
                }
            }
        },
        []
    );

    const cancelStream = useCallback(() =>
    {
        if (abortControllerRef.current)
        {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
        setIsStreaming(false);
        setCurrentStatus('');
    }, []);

    return {
        sendMessage,
        cancelStream,
        isStreaming,
        currentStatus,
    };
}

