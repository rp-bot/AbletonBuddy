/**
 * List of conversation threads
 */

import { ThreadItem } from "./ThreadItem";
import type { ThreadSummary } from "@/api/types";

interface ThreadListProps {
  threads: ThreadSummary[];
  activeThreadId: string | null;
  onSelectThread: (threadId: string) => void;
  onDeleteThread?: (threadId: string) => void;
}

export function ThreadList({ threads, activeThreadId, onSelectThread, onDeleteThread }: ThreadListProps) {
  if (threads.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 text-gray-500">
        <p className="text-sm">No conversations yet</p>
        <p className="text-xs mt-2">Create a new thread to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-4 overflow-y-auto">
      {threads.map((thread) => (
        <ThreadItem
          key={thread.thread_id}
          thread={thread}
          isActive={thread.thread_id === activeThreadId}
          onClick={() => onSelectThread(thread.thread_id)}
          onDelete={onDeleteThread}
        />
      ))}
    </div>
  );
}
