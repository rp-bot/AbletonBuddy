import { useState } from "react";
import { getAgentStepsSummary, isAgentStepsProcessing } from "../../utils/messageGrouper";
import StreamingStatus from "./StreamingStatus";

/**
 * Collapsible dropdown component for displaying agent processing steps
 * Similar to ChatGPT and Gemini's chain-of-thought UI
 */
export default function AgentStepsDropdown({
  agentSteps,
  isStreaming = false,
  messageContent = "",
  messageType = "assistant",
  statusMessage = "",
  streamingEvents = [],
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!agentSteps && !isStreaming) {
    return null;
  }

  const isCancelled = messageContent === "Generation stopped by user";
  const isClarification = messageType === "clarification" || messageContent.startsWith("I need more information to help you");
  const summary = isCancelled
    ? "Generation cancelled"
    : isClarification
    ? "Clarification requested"
    : agentSteps
    ? getAgentStepsSummary(agentSteps)
    : "Processing...";
  const isProcessing =
    !isCancelled &&
    !isClarification &&
    (isStreaming || (agentSteps && isAgentStepsProcessing(agentSteps, messageContent, messageType)));

  // Show streaming status component during active streaming
  if (isStreaming && isProcessing) {
    return (
      <div className="mb-2">
        <StreamingStatus agentSteps={agentSteps} isStreaming={isStreaming} statusMessage={statusMessage} streamingEvents={streamingEvents} />
      </div>
    );
  }

  return (
    <div className="mb-2">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center space-x-2">
          {isProcessing ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          ) : isCancelled ? (
            <div className="w-4 h-4 flex items-center justify-center">
              <svg className="w-4 h-4 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          ) : isClarification ? (
            <div className="w-4 h-4 flex items-center justify-center">
              <svg className="w-4 h-4 text-yellow-500 dark:text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M12 18a9 9 0 110-18 9 9 0 010 18z" />
              </svg>
            </div>
          ) : (
            <div className="w-4 h-4 flex items-center justify-center">
              <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          )}
          <span className={`text-base font-medium ${isCancelled ? "text-red-700 dark:text-red-300" : "text-gray-700 dark:text-gray-300"}`}>{summary}</span>
        </div>
        <div className={`transform transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}>
          <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-2 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 animate-in slide-in-from-top-2 duration-200">
          {agentSteps ? (
            <div className="space-y-4">
              {/* Disambiguation */}
              {agentSteps.disambiguation && (
                <div className="border-l-4 border-blue-400 pl-3">
                  <h4 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Understanding</h4>
                  <p className="text-base text-gray-600 dark:text-gray-400">{agentSteps.disambiguation.data}</p>
                </div>
              )}

              {/* Classification */}
              {agentSteps.classification && (
                <div className="border-l-4 border-green-400 pl-3">
                  <h4 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Classification</h4>
                  <p className="text-base text-gray-600 dark:text-gray-400">{agentSteps.classification.data}</p>
                </div>
              )}

              {/* Extraction */}
              {agentSteps.extraction && (
                <div className="border-l-4 border-yellow-400 pl-3">
                  <h4 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Extraction</h4>
                  <p className="text-base text-gray-600 dark:text-gray-400">{agentSteps.extraction.data}</p>
                </div>
              )}

              {/* Status Updates - Commented out to hide after streaming */}
              {/* {agentSteps.status && agentSteps.status.length > 0 && (
                <div className="border-l-4 border-gray-400 pl-3">
                  <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">Status Updates</h4>
                  <div className="space-y-1">
                    {agentSteps.status.map((status, index) => (
                      <div key={index} className="text-sm text-gray-600 dark:text-gray-400">
                        • {status.data}
                      </div>
                    ))}
                  </div>
                </div>
              )} */}

              {/* Task Execution */}
              {agentSteps.tasks && agentSteps.tasks.length > 0 && (
                <div className="border-l-4 border-purple-400 pl-3">
                  <h4 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-2">Task Execution</h4>
                  <div className="space-y-2">
                    {agentSteps.tasks.map((task, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div
                          className={`w-2 h-2 rounded-full mt-2 ${
                            task.status === "success" ? "bg-green-500" : task.status === "failed" ? "bg-red-500" : "bg-yellow-500"
                          }`}
                        ></div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-base font-medium text-gray-800 dark:text-gray-200">{task.name}</span>
                            <span
                              className={`px-2 py-1 text-sm rounded-full ${
                                task.status === "success"
                                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                  : task.status === "failed"
                                  ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                                  : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                              }`}
                            >
                              {task.status}
                            </span>
                          </div>
                          {task.result && <p className="text-base text-gray-600 dark:text-gray-400 mt-1">{task.result}</p>}
                          {task.tools && task.tools.length > 0 && (
                            <div className="mt-1">
                              <span className="text-sm text-gray-500 dark:text-gray-500">Tools: {task.tools.join(", ")}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cancellation Step */}
              {isCancelled && (
                <div className="border-l-4 border-red-400 pl-3">
                  <h4 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Cancellation</h4>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 rounded-full mt-2 bg-red-500"></div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-medium text-gray-800 dark:text-gray-200">Generation stopped by user</span>
                        <span className="px-2 py-1 text-sm rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">cancelled</span>
                      </div>
                      <p className="text-base text-gray-600 dark:text-gray-400 mt-1">Processing was interrupted before completion</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-base text-gray-600 dark:text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span>Processing your request...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
