import { useState, useCallback } from "react";
import { streamMessage } from "../api/client";

/**
 * Custom hook for managing streaming chat functionality
 * @param {string} threadId - Current thread ID
 * @param {Function} onMessageUpdate - Callback when messages are updated
 */
export function useStreamingChat(threadId, onMessageUpdate) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [streamingEvents, setStreamingEvents] = useState([]);

  /**
   * Send a message and handle streaming response
   * @param {string} content - Message content
   */
  const sendMessage = useCallback(
    async (content) => {
      if (!threadId || !content.trim()) return;

      setIsStreaming(true);
      setStatusMessage("Processing your request...");
      setStreamingEvents([]);

      try {
        await streamMessage(threadId, content, (event) => {
          handleStreamingEvent(event);
        });
      } catch (error) {
        console.error("Streaming error:", error);
        setStatusMessage("Error: " + error.message);
      } finally {
        setIsStreaming(false);
        setStatusMessage("");
        setStreamingEvents([]);
      }
    },
    [threadId],
  );

  /**
   * Handle individual streaming events
   * @param {Object} event - SSE event data
   */
  const handleStreamingEvent = (event) => {
    const { event: eventType, data } = event;

    // Add to streaming events log
    setStreamingEvents((prev) => [...prev, { type: eventType, data, timestamp: new Date() }]);

    switch (eventType) {
      case "status":
        setStatusMessage(data);
        break;

      case "disambiguation":
        setStatusMessage(`Understanding: ${data}`);
        break;

      case "classification":
        setStatusMessage(`Identifying operations: ${data}`);
        break;

      case "extraction":
        setStatusMessage(`Extracting operations: ${data}`);
        break;

      case "task_success":
        setStatusMessage(`Task completed: ${data}`);
        break;

      case "task_skipped":
        setStatusMessage(`Task skipped: ${data}`);
        break;

      case "task_failed":
        setStatusMessage(`Task failed: ${data}`);
        break;

      case "assistant":
        // Final response - add to messages and clear status
        setStatusMessage("");
        if (onMessageUpdate) {
          onMessageUpdate({
            id: Date.now().toString(),
            role: "assistant",
            content: data,
            timestamp: new Date().toISOString(),
          });
        }
        break;

      case "done":
        setStatusMessage("");
        break;

      case "error":
        setStatusMessage(`Error: ${data}`);
        break;

      default:
        console.log("Unknown event type:", eventType, data);
    }
  };

  /**
   * Clear current streaming status
   */
  const clearStatus = useCallback(() => {
    setStatusMessage("");
    setStreamingEvents([]);
  }, []);

  return {
    isStreaming,
    statusMessage,
    streamingEvents,
    sendMessage,
    clearStatus,
  };
}
