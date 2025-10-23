/**
 * Individual thread item in the sidebar
 */

import type { ThreadSummary } from "@/api/types";

interface ThreadItemProps {
  thread: ThreadSummary;
  isActive: boolean;
  onClick: () => void;
  onDelete?: (threadId: string) => void;
}

export function ThreadItem({ thread, isActive, onClick, onDelete }: ThreadItemProps) {
  const formattedDate = new Date(thread.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(thread.thread_id);
    }
  };

  return (
    <div className="group relative">
      <button
        onClick={onClick}
        className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
          isActive ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
        }`}
      >
        <div className="flex justify-between items-start mb-1">
          <span className="text-xs font-medium opacity-75">{formattedDate}</span>
          <span className="text-xs opacity-75">{thread.message_count} msgs</span>
        </div>
        <p className="text-sm line-clamp-2">{thread.summary}</p>
      </button>
      {onDelete && (
        <button
          onClick={handleDelete}
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full hover:bg-red-100 text-red-500 hover:text-red-700"
          title="Delete thread"
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
      )}
    </div>
  );
}
