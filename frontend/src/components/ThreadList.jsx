import { useState, useEffect } from "react";
import { listThreads, createThread, deleteThread } from "../api/client";
import { getDisplayMessageCount, getThreadPreview } from "../utils/messageFilter";

/**
 * Thread list component for sidebar
 */
export default function ThreadList({ onThreadSelect, currentThreadId }) {
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadThreads();
  }, []);

  const loadThreads = async () => {
    try {
      setLoading(true);
      setError(null);
      const threadData = await listThreads();
      setThreads(threadData);
    } catch (err) {
      setError("Failed to load threads");
      console.error("Error loading threads:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateThread = async () => {
    try {
      const newThread = await createThread();
      // Reload threads to get the new one
      await loadThreads();
      // Select the new thread
      onThreadSelect(newThread.thread_id);
    } catch (err) {
      setError("Failed to create thread");
      console.error("Error creating thread:", err);
    }
  };

  const handleDeleteThread = async (threadId, event) => {
    event.stopPropagation(); // Prevent thread selection

    if (window.confirm("Are you sure you want to delete this conversation? This action cannot be undone.")) {
      try {
        await deleteThread(threadId);
        // Reload threads to remove the deleted one
        await loadThreads();
        // If the deleted thread was currently selected, clear selection
        if (currentThreadId === threadId) {
          onThreadSelect(null);
        }
      } catch (err) {
        setError("Failed to delete thread");
        console.error("Error deleting thread:", err);
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return "Just now";
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-red-600 dark:text-red-400 text-sm mb-2">{error}</div>
        <button onClick={loadThreads} className="text-blue-600 dark:text-blue-400 text-sm hover:underline">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button onClick={handleCreateThread} className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
          + New Thread
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {threads.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Create your first thread to get started</p>
          </div>
        ) : (
          <div className="p-2">
            {threads.map((thread) => (
              <div
                key={thread.thread_id}
                className={`p-3 rounded-lg cursor-pointer transition-colors mb-2 group ${
                  currentThreadId === thread.thread_id
                    ? "bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-700"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <div className="flex-1 cursor-pointer" onClick={() => onThreadSelect(thread.thread_id)}>
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate" title={thread.summary || "New conversation"}>
                      {(thread.summary || "New conversation").length > 20
                        ? (thread.summary || "New conversation").substring(0, 20) + "..."
                        : thread.summary || "New conversation"}
                    </h3>
                  </div>
                  <div className="flex items-center space-x-2 ml-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400 shrink-0">{formatDate(thread.created_at)}</span>
                    <button
                      onClick={(e) => handleDeleteThread(thread.thread_id, e)}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity p-1"
                      title="Delete conversation"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 dark:text-gray-400">{thread.message_count} messages</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
