import { useState, useEffect } from "react";
import { MainContainer, ChatContainer as ChatScopeChatContainer } from "@chatscope/chat-ui-kit-react";
import { getThreadDetailed } from "../../api/client";
import { useStreamingChat } from "../../hooks/useStreamingChat";
import MessageList from "./MessageList";
import InputArea from "./InputArea";
import StatusIndicator from "./StatusIndicator";

/**
 * Main chat container component
 */
export default function ChatContainer({ threadId, showDetails }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { isStreaming, statusMessage, streamingEvents, sendMessage } = useStreamingChat(threadId, (newMessage) => {
    setMessages((prev) => [...prev, newMessage]);
  });

  useEffect(() => {
    if (threadId) {
      loadThreadMessages();
    }
  }, [threadId]);

  const loadThreadMessages = async () => {
    try {
      setLoading(true);
      setError(null);
      const threadData = await getThreadDetailed(threadId);
      setMessages(threadData.messages || []);
    } catch (err) {
      setError("Failed to load messages");
      console.error("Error loading thread:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content) => {
    if (!threadId || !content.trim()) return;

    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send message and handle streaming
    await sendMessage(content);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button onClick={loadThreadMessages} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="flex-1 flex flex-col h-full">
        {/* Status Indicator */}
        <StatusIndicator statusMessage={statusMessage} isStreaming={isStreaming} streamingEvents={streamingEvents} />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No messages yet</h3>
                <p className="text-gray-600 dark:text-gray-400">Start a conversation by typing a message below.</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"
                    }`}
                  >
                    <div className="text-sm font-medium mb-1">{message.role === "user" ? "You" : "Ableton Buddy"}</div>
                    <div className="text-sm">{message.content}</div>
                    <div className="text-xs opacity-70 mt-1">{new Date(message.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Type your message..."
              className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSendMessage(e.target.value);
                  e.target.value = "";
                }
              }}
            />
            <button
              onClick={() => {
                const input = document.querySelector("input");
                if (input.value) {
                  handleSendMessage(input.value);
                  input.value = "";
                }
              }}
              disabled={isStreaming}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isStreaming ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
