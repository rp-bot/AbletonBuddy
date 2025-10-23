/**
 * Sidebar containing thread history and controls
 */

import { ThreadList } from "./ThreadList";
import { useThreads, useCreateThread, useDeleteThread } from "@/hooks/useThreads";

interface ThreadSidebarProps {
  activeThreadId: string | null;
  onSelectThread: (threadId: string) => void;
}

export function ThreadSidebar({ activeThreadId, onSelectThread }: ThreadSidebarProps) {
  const { data: threads, isLoading, error } = useThreads();
  const createThreadMutation = useCreateThread();
  const deleteThreadMutation = useDeleteThread();

  const handleCreateThread = async () => {
    try {
      const newThread = await createThreadMutation.mutateAsync();
      onSelectThread(newThread.thread_id);
    } catch (error) {
      console.error("Failed to create thread:", error);
    }
  };

  const handleDeleteThread = async (threadId: string) => {
    if (window.confirm("Are you sure you want to delete this conversation? This action cannot be undone.")) {
      try {
        await deleteThreadMutation.mutateAsync(threadId);
        // If we're deleting the currently active thread, clear the selection
        if (activeThreadId === threadId) {
          onSelectThread("");
        }
      } catch (error) {
        console.error("Failed to delete thread:", error);
      }
    }
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800 mb-4">Ableton Buddy</h1>
        <button
          onClick={handleCreateThread}
          disabled={createThreadMutation.isPending}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createThreadMutation.isPending ? "Creating..." : "+ New Conversation"}
        </button>
      </div>

      {/* Thread List */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">Loading threads...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-500 text-sm px-4 text-center">Error loading threads. Make sure the backend is running.</div>
          </div>
        ) : (
          <ThreadList threads={threads || []} activeThreadId={activeThreadId} onSelectThread={onSelectThread} onDeleteThread={handleDeleteThread} />
        )}
      </div>
    </div>
  );
}
