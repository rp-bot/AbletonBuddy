import { useState, useCallback, useRef } from "react";
import { streamMessage, cancelStream } from "../api/client";

/**
 * Custom hook for managing streaming chat functionality
 * @param {string} threadId - Current thread ID
 * @param {Function} onMessageUpdate - Callback when messages are updated (for adding new messages)
 */
export function useStreamingChat(threadId, onMessageUpdate) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [streamingEvents, setStreamingEvents] = useState([]);
  const [accumulatedAgentSteps, setAccumulatedAgentSteps] = useState([]);
  const abortControllerRef = useRef(null);
  const streamAbortRef = useRef(null);
  // const [currentPlaceholderId, setCurrentPlaceholderId] = useState(null);

  /**
   * Send a message and handle streaming response
   * @param {string} content - Message content
   * @param {string} placeholderId - ID of the placeholder message to update
   */
  const sendMessage = useCallback(
    async (content, placeholderId) => {
      if (!threadId || !content.trim()) return;

      // Create new AbortController for this request
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setIsStreaming(true);
      setStatusMessage("Processing your request...");
      setStreamingEvents([]);
      setAccumulatedAgentSteps([]);

      try {
        const streamResult = await streamMessage(
          threadId,
          content,
          (event) => {
            handleStreamingEvent(event, placeholderId);
          },
          abortController.signal,
        );

        // Store the abort function for external cancellation
        streamAbortRef.current = streamResult.abort;
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Stream was cancelled");
          setStatusMessage("Generation stopped by user");
        } else {
          console.error("Streaming error:", error);
          setStatusMessage("Error: " + error.message);
        }
      } finally {
        setIsStreaming(false);
        setStatusMessage("");
        setStreamingEvents([]);
        abortControllerRef.current = null;
        streamAbortRef.current = null;
        // Don't clear accumulated steps here - they're needed for the final message
        // setAccumulatedAgentSteps([]);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [threadId],
  );

  /**
   * Handle individual streaming events
   * @param {Object} event - SSE event data
   * @param {string} placeholderId - ID of placeholder message to update
   */
  const handleStreamingEvent = (event, placeholderId) => {
    const { event: eventType, data } = event;

    // Add to streaming events log
    setStreamingEvents((prev) => [...prev, { type: eventType, data, timestamp: new Date() }]);

    // Accumulate agent steps for the final message
    if (isAgentStepEvent(eventType)) {
      const newStep = {
        role: eventType,
        content: data,
        timestamp: new Date().toISOString(),
      };

      // Update accumulated steps and immediately update the UI
      setAccumulatedAgentSteps((prev) => {
        const newAccumulatedSteps = [...prev, newStep];

        // Update placeholder message with new agent step in real-time
        if (onMessageUpdate && placeholderId) {
          onMessageUpdate((prevMessages) =>
            prevMessages.map((msg) => {
              if (msg.id === placeholderId) {
                const updatedAgentSteps = parseAccumulatedAgentSteps(newAccumulatedSteps);
                return {
                  ...msg,
                  agentSteps: updatedAgentSteps,
                  isStreaming: true,
                };
              }
              return msg;
            }),
          );
        }

        return newAccumulatedSteps;
      });
    }

    switch (eventType) {
      case "status":
        setStatusMessage(data);
        break;

      case "disambiguation":
        setStatusMessage("Clarifying your request...");
        break;

      case "classification":
        setStatusMessage("Classifying operations...");
        break;

      case "extraction":
        setStatusMessage("Extracting details...");
        break;

      case "task_success":
        setStatusMessage("Executing tasks...");
        break;

      case "task_skipped":
        setStatusMessage("Skipping task...");
        break;

      case "task_failed":
        setStatusMessage("Handling task error...");
        break;

      case "assistant":
        // Final response - update placeholder message with content
        setStatusMessage("Finalizing response...");
        if (onMessageUpdate && placeholderId) {
          // Use the current accumulated steps before they get cleared
          const currentSteps = [...accumulatedAgentSteps];
          const parsedSteps = parseAccumulatedAgentSteps(currentSteps);

          // Remove "Summarization Agent:" prefix if present (like backend does)
          const cleanContent = data.replace("Summarization Agent:", "").trim();
          const isClarification = cleanContent.startsWith("I need more information to help you");

          onMessageUpdate((prevMessages) =>
            prevMessages.map((msg) => {
              if (msg.id === placeholderId) {
                return {
                  ...msg,
                  content: cleanContent,
                  agentSteps: parsedSteps,
                  isStreaming: false,
                  messageType: isClarification ? "clarification" : "assistant",
                };
              }
              return msg;
            }),
          );
          // Clear accumulated steps after updating the message
          setAccumulatedAgentSteps([]);
        }
        break;

      case "done":
        setStatusMessage("");
        // Reload thread data to get persisted agent steps
        setTimeout(() => {
          reloadThreadData();
        }, 1000); // Small delay to ensure backend has finished saving
        break;

      case "cancelled":
        setStatusMessage("");
        // Update message with accumulated steps and cancelled content
        if (onMessageUpdate && placeholderId) {
          const currentSteps = [...accumulatedAgentSteps];
          const parsedSteps = parseAccumulatedAgentSteps(currentSteps);

          // Remove "Summarization Agent:" prefix if present (like backend does)
          const cleanContent = data.replace("Summarization Agent:", "").trim();

          onMessageUpdate((prevMessages) =>
            prevMessages.map((msg) => {
              if (msg.id === placeholderId) {
                return {
                  ...msg,
                  content: cleanContent,
                  agentSteps: parsedSteps,
                  isStreaming: false,
                  messageType: "assistant",
                };
              }
              return msg;
            }),
          );
          setAccumulatedAgentSteps([]);
        }
        // Reload thread data to get persisted state
        setTimeout(() => {
          reloadThreadData();
        }, 1000);
        break;

      case "error":
        setStatusMessage(`Error: ${data}`);
        break;

      default:
        console.log("Unknown event type:", eventType, data);
    }
  };

  /**
   * Check if an event type represents an agent processing step
   * @param {string} eventType - Event type
   * @returns {boolean} True if it's an agent step
   */
  const isAgentStepEvent = (eventType) => {
    return ["status", "disambiguation", "classification", "extraction", "task_success", "task_failed", "task_skipped"].includes(eventType);
  };

  /**
   * Parse accumulated agent steps into structured format
   * @param {Array} steps - Accumulated agent steps
   * @returns {Object} Structured agent steps
   */
  const parseAccumulatedAgentSteps = (steps) => {
    const agentSteps = {
      status: [],
      disambiguation: null,
      classification: null,
      extraction: null,
      tasks: [],
    };

    for (const step of steps) {
      const { role, content, timestamp } = step;

      switch (role) {
        case "status":
          agentSteps.status.push({
            data: content,
            timestamp: timestamp,
          });
          break;

        case "disambiguation":
          agentSteps.disambiguation = {
            data: content,
            timestamp: timestamp,
          };
          break;

        case "classification":
          agentSteps.classification = {
            data: content,
            timestamp: timestamp,
          };
          break;

        case "extraction":
          agentSteps.extraction = {
            data: content,
            timestamp: timestamp,
          };
          break;

        case "task_success":
        case "task_failed":
        case "task_skipped": {
          const task = parseTaskFromEvent(content, role, timestamp);
          if (task) {
            agentSteps.tasks.push(task);
          }
          break;
        }
      }
    }

    return agentSteps;
  };

  /**
   * Parse task from streaming event
   * @param {string} content - Task content
   * @param {string} role - Task role
   * @param {string} timestamp - Timestamp
   * @returns {Object|null} Parsed task
   */
  const parseTaskFromEvent = (content, role, timestamp) => {
    try {
      // Extract task name and result from content
      const taskName = content.split(": ")[1]?.split(" ")[0] || "Unknown Task";
      const taskResult = content.split(" ").slice(2).join(" ") || "";

      return {
        name: taskName,
        status: role.replace("task_", ""),
        result: taskResult,
        tools: [],
        timestamp: timestamp,
      };
    } catch (error) {
      console.warn("Failed to parse task from event:", content, error);
      return null;
    }
  };

  /**
   * Cancel the current stream
   */
  const cancelCurrentStream = useCallback(async () => {
    if (abortControllerRef.current) {
      // Cancel the frontend request
      abortControllerRef.current.abort();
    }

    if (streamAbortRef.current) {
      // Cancel the backend processing
      await streamAbortRef.current();
    }

    // Also call the backend directly as a fallback
    try {
      await cancelStream(threadId);
    } catch (error) {
      console.warn("Failed to cancel stream:", error);
    }
  }, [threadId]);

  /**
   * Clear current streaming status
   */
  const clearStatus = useCallback(() => {
    setStatusMessage("");
    setStreamingEvents([]);
  }, []);

  /**
   * Reload thread data after streaming completes
   */
  const reloadThreadData = useCallback(async () => {
    if (threadId && onMessageUpdate) {
      try {
        const response = await fetch(`http://localhost:8000/threads/${threadId}/detailed`);
        if (response.ok) {
          const threadData = await response.json();
          const { groupMessagesWithAgentSteps } = await import("../utils/messageGrouper");
          const groupedMessages = groupMessagesWithAgentSteps(threadData.messages || []);
          onMessageUpdate(() => groupedMessages);
        }
      } catch (error) {
        console.error("Failed to reload thread data:", error);
      }
    }
  }, [threadId, onMessageUpdate]);

  return {
    isStreaming,
    statusMessage,
    streamingEvents,
    sendMessage,
    cancelStream: cancelCurrentStream,
    clearStatus,
    reloadThreadData,
  };
}
