/**
 * API client for Ableton Buddy backend
 */

const API_BASE_URL = "http://localhost:8000";

/**
 * List all conversation threads
 * @returns {Promise<Array>} Array of thread summaries
 */
export async function listThreads() {
  const response = await fetch(`${API_BASE_URL}/threads`);
  if (!response.ok) {
    throw new Error("Failed to fetch threads");
  }
  return response.json();
}

/**
 * Create a new conversation thread
 * @returns {Promise<Object>} New thread object with thread_id
 */
export async function createThread() {
  const response = await fetch(`${API_BASE_URL}/threads`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to create thread");
  }
  return response.json();
}

/**
 * Get detailed thread information with all messages
 * @param {string} threadId - Thread ID
 * @returns {Promise<Object>} Thread details with messages
 */
export async function getThreadDetailed(threadId) {
  const response = await fetch(`${API_BASE_URL}/threads/${threadId}/detailed`);
  if (!response.ok) {
    throw new Error("Failed to fetch thread details");
  }
  return response.json();
}

/**
 * Stream a message to a thread and get real-time updates
 * @param {string} threadId - Thread ID
 * @param {string} content - Message content
 * @param {Function} onEvent - Callback for each SSE event
 * @param {AbortSignal} signal - Abort signal for cancellation
 * @returns {Promise<{abort: Function}>} Object with abort function
 */
export async function streamMessage(threadId, content, onEvent, signal) {
  const response = await fetch(`${API_BASE_URL}/threads/${threadId}/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
    signal: signal,
  });

  if (!response.ok) {
    throw new Error("Failed to stream message");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEventType = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete events in the buffer
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          // Store the event type for the next data line
          currentEventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          // Extract the data payload (plain string, not JSON)
          const data = line.slice(6).trim();

          // Combine event type and data into the expected format
          if (currentEventType) {
            const event = {
              event: currentEventType,
              data: data,
            };
            onEvent(event);
          }

          // Reset for next event
          currentEventType = "";
        } else if (line.trim() === "") {
          // Empty line indicates end of SSE message
          // Reset state for next message
          currentEventType = "";
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  // Return abort function that calls the backend cancellation endpoint
  return {
    abort: async () => {
      try {
        await fetch(`${API_BASE_URL}/threads/${threadId}/stream`, {
          method: "DELETE",
        });
      } catch (error) {
        console.warn("Failed to cancel stream on backend:", error);
      }
    },
  };
}

/**
 * Cancel an active stream for a thread
 * @param {string} threadId - Thread ID
 * @returns {Promise<Object>} Success message
 */
export async function cancelStream(threadId) {
  const response = await fetch(`${API_BASE_URL}/threads/${threadId}/stream`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to cancel stream");
  }
  return response.json();
}

/**
 * Delete a thread
 * @param {string} threadId - Thread ID
 * @returns {Promise<Object>} Success message
 */
export async function deleteThread(threadId) {
  const response = await fetch(`${API_BASE_URL}/threads/${threadId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete thread");
  }
  return response.json();
}
