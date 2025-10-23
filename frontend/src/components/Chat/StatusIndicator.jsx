/**
 * Status indicator component for streaming events
 */
export default function StatusIndicator({ statusMessage, isStreaming, streamingEvents }) {
  if (!isStreaming && !statusMessage) {
    return null;
  }

  return (
    <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400">
      <div className="flex items-center">
        {isStreaming && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>}
        <div className="flex-1">
          <p className="text-sm text-blue-800 dark:text-blue-200">{statusMessage}</p>
          {streamingEvents.length > 0 && (
            <div className="mt-1 text-xs text-blue-600 dark:text-blue-300">
              {streamingEvents.length} event{streamingEvents.length !== 1 ? "s" : ""} processed
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
