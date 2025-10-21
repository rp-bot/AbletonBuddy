# API Integration Guide

This guide shows how to integrate the Ableton Buddy API with a React frontend.

## Starting the API Server

```bash
python3 run_api.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Endpoints

### 1. Create a New Thread

```javascript
const createThread = async () => {
  const response = await fetch("http://localhost:8000/threads", {
    method: "POST",
  });
  const data = await response.json();
  return data.thread_id;
};
```

### 2. Get Thread History

```javascript
const getThread = async (threadId) => {
  const response = await fetch(`http://localhost:8000/threads/${threadId}`);
  const data = await response.json();
  return data;
};
```

### 3. Send a Message (Simple)

```javascript
const sendMessage = async (threadId, content) => {
  const response = await fetch(`http://localhost:8000/threads/${threadId}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });
  const data = await response.json();
  return data;
};
```

### 4. Send a Message with Streaming (Recommended)

This endpoint uses Server-Sent Events (SSE) to stream real-time updates as the agent processes the request.

```javascript
const sendMessageStreaming = (threadId, content, callbacks) => {
  const eventSource = new EventSource(
    `http://localhost:8000/threads/${threadId}/stream?${new URLSearchParams({
      content,
    })}`,
  );

  // Handle status updates (agent is processing)
  eventSource.addEventListener("status", (event) => {
    callbacks.onStatus?.(event.data);
    // Examples: "Processing your request...", "Executing tasks...", etc.
  });

  // Handle the final message
  eventSource.addEventListener("message", (event) => {
    callbacks.onMessage?.(event.data);
  });

  // Handle completion
  eventSource.addEventListener("done", (event) => {
    callbacks.onDone?.(event.data);
    eventSource.close();
  });

  // Handle errors
  eventSource.addEventListener("error", (event) => {
    callbacks.onError?.(event.data);
    eventSource.close();
  });

  eventSource.onerror = (error) => {
    console.error("SSE error:", error);
    callbacks.onError?.(error);
    eventSource.close();
  };

  return eventSource;
};
```

## React Example

Here's a complete React component example:

```jsx
import React, { useState, useEffect } from "react";

function AbletonChat() {
  const [threadId, setThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  // Create a thread on mount
  useEffect(() => {
    const initThread = async () => {
      const response = await fetch("http://localhost:8000/threads", {
        method: "POST",
      });
      const data = await response.json();
      setThreadId(data.thread_id);
    };
    initThread();
  }, []);

  const sendMessage = () => {
    if (!input.trim() || !threadId) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setStatus("Processing...");

    // Use streaming endpoint
    const eventSource = new EventSource(`http://localhost:8000/threads/${threadId}/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: input }),
    });

    eventSource.addEventListener("status", (event) => {
      setStatus(event.data);
    });

    eventSource.addEventListener("message", (event) => {
      const assistantMessage = { role: "assistant", content: event.data };
      setMessages((prev) => [...prev, assistantMessage]);
      setStatus("");
    });

    eventSource.addEventListener("done", () => {
      setLoading(false);
      eventSource.close();
    });

    eventSource.addEventListener("error", (event) => {
      console.error("Error:", event.data);
      setStatus("Error occurred");
      setLoading(false);
      eventSource.close();
    });
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role === "user" ? "You" : "Assistant"}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
        {status && <div className="status">{status}</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Enter command..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default AbletonChat;
```

## Response Format

### Message Response

```json
{
  "id": "message-uuid",
  "role": "assistant",
  "content": "Track 1 has been successfully soloed.",
  "timestamp": "2025-10-21T17:13:18.087317"
}
```

### Thread Detail Response

```json
{
  "thread_id": "thread-uuid",
  "created_at": "2025-10-21T17:13:05.788070",
  "messages": [
    {
      "id": "msg-1-uuid",
      "role": "user",
      "content": "can you solo track 1",
      "timestamp": "2025-10-21T17:13:05.788070"
    },
    {
      "id": "msg-2-uuid",
      "role": "assistant",
      "content": "• The user asked me to solo track 1 in an Ableton Live session.\n• I successfully processed the task, identified the request precisely, and soloed track 1.\n• Key outcome: Track 1 was soloed, ensuring that only it plays while all other tracks are muted.\n• The request was completed successfully.\n\nDo you need me to do anything else?",
      "timestamp": "2025-10-21T17:13:18.087317"
    }
  ]
}
```

### SSE Event Types

1. **status**: Processing updates

   - `"Processing your request..."`
   - `"Understanding your command..."`
   - `"Identifying operations..."`
   - `"Creating tasks..."`
   - `"Executing 2 task(s)..."`
   - `"Running task 1/2: TRACK Task"`
   - `"Preparing response..."`

2. **message**: The final assistant response

   - Contains the summarized result

3. **done**: Signals completion

   - `"Complete"` or `"Need clarification"`

4. **error**: Error occurred
   - Contains error message

## Notes

- All conversations are automatically persisted to the SQLite database
- Messages are filtered to show only user messages and final assistant summaries
- Internal processing messages (classification, extraction, task execution) are hidden by default
- The streaming endpoint provides real-time status updates for better UX
