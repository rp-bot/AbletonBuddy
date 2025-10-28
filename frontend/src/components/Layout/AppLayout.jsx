import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ThreadList from "../ThreadList";
import ChatContainer from "../Chat/ChatContainer";

/**
 * Main application layout with sidebar and chat area
 */
export default function AppLayout() {
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Extract threadId from URL
  useEffect(() => {
    const pathParts = location.pathname.split("/");
    const threadId = pathParts[1] === "thread" ? pathParts[2] : null;
    setCurrentThreadId(threadId);
  }, [location.pathname]);

  const handleThreadSelect = (threadId) => {
    if (threadId) {
      setCurrentThreadId(threadId);
      navigate(`/thread/${threadId}`);
    } else {
      setCurrentThreadId(null);
      navigate("/");
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Ableton Buddy</h1>
        </div>

        <div className="flex-1 overflow-hidden">
          <ThreadList onThreadSelect={handleThreadSelect} currentThreadId={currentThreadId} />
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentThreadId ? (
          <ChatContainer threadId={currentThreadId} />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Welcome to Ableton Buddy</h2>
              <p className="text-gray-600 dark:text-gray-400">Select a thread from the sidebar or create a new one to get started.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
