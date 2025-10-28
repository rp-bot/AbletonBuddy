import { useState, useEffect } from "react";

/**
 * Streaming status component that shows dynamic status messages with animations
 * during the agent processing pipeline
 */
export default function StreamingStatus({ agentSteps, isStreaming, statusMessage, streamingEvents = [] }) {
  const [currentStatus, setCurrentStatus] = useState("");
  const [statusHistory, setStatusHistory] = useState([]);

  // Define the processing stages with their display messages
  const processingStages = {
    initial: "Understanding your input...",
    disambiguation: "Clarifying your request...",
    classification: "Classifying operations...",
    extraction: "Extracting details...",
    task_execution: "Executing tasks...",
    completion: "Finalizing response...",
  };

  // Update status based on agent steps and streaming events
  useEffect(() => {
    if (!isStreaming) {
      setCurrentStatus("");
      setStatusHistory([]);
      return;
    }

    let newStatus = processingStages.initial;

    // Check for specific processing stages
    if (agentSteps) {
      if (agentSteps.disambiguation) {
        newStatus = processingStages.disambiguation;
      } else if (agentSteps.classification) {
        newStatus = processingStages.classification;
      } else if (agentSteps.extraction) {
        newStatus = processingStages.extraction;
      } else if (agentSteps.tasks && agentSteps.tasks.length > 0) {
        newStatus = processingStages.task_execution;
      }
    }

    // Use custom status message if available
    if (statusMessage) {
      newStatus = statusMessage;
    }

    // Add to history if status changed
    if (newStatus !== currentStatus) {
      setStatusHistory((prev) => [...prev, { status: newStatus, timestamp: Date.now() }]);
      setCurrentStatus(newStatus);
    }
  }, [agentSteps, isStreaming, statusMessage, currentStatus]);

  if (!isStreaming || !currentStatus) {
    return null;
  }

  return (
    <div className="flex items-center space-x-3 px-4 py-3 bg-linear-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-l-4 border-blue-400 rounded-r-lg">
      {/* Animated spinner */}
      <div className="relative">
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-200 dark:border-blue-700"></div>
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent absolute top-0 left-0"></div>
      </div>

      {/* Status text with animation */}
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-blue-800 dark:text-blue-200 animate-pulse">{currentStatus}</span>

          {/* Dots animation */}
          <div className="flex space-x-1">
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
          </div>
        </div>

        {/* Progress indicator */}
        {statusHistory.length > 1 && <div className="mt-1 text-xs text-blue-600 dark:text-blue-400">Step {statusHistory.length} of processing</div>}
      </div>

      {/* Processing indicator */}
      <div className="flex items-center space-x-1 text-xs text-blue-600 dark:text-blue-400">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
        <span>Processing</span>
      </div>
    </div>
  );
}
