/**
 * Main application layout with sidebar and chat area
 */

import { useState } from "react";
import { ThreadSidebar } from "../Sidebar/ThreadSidebar";
import { ChatContainer } from "../Chat/ChatContainer";

export function AppLayout() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);

  return (
    <div className="flex h-screen overflow-hidden">
      <ThreadSidebar activeThreadId={activeThreadId} onSelectThread={setActiveThreadId} />
      <ChatContainer threadId={activeThreadId} />
    </div>
  );
}
