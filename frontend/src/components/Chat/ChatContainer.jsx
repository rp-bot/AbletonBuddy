import { useState, useEffect, useCallback } from "react";
import { MainContainer, ChatContainer as ChatScopeChatContainer } from "@chatscope/chat-ui-kit-react";
import { getThreadDetailed } from "../../api/client";
import { useStreamingChat } from "../../hooks/useStreamingChat";
import { groupMessagesWithAgentSteps } from "../../utils/messageGrouper";
import MessageList from "./MessageList";
import InputArea from "./InputArea";
import AgentStepsDropdown from "./AgentStepsDropdown";

/**
 * Main chat container component
 */
export default function ChatContainer({ threadId }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { isStreaming, sendMessage } = useStreamingChat(threadId, (updateFn) => {
    setMessages(updateFn);
  });

  useEffect(() => {
    if (threadId) {
      loadThreadMessages();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threadId]);

  const loadThreadMessages = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const threadData = await getThreadDetailed(threadId);
      // Group messages with agent steps for proper display
      const groupedMessages = groupMessagesWithAgentSteps(threadData.messages || []);
      setMessages(groupedMessages);
    } catch (err) {
      setError("Failed to load messages");
      console.error("Error loading thread:", err);
    } finally {
      setLoading(false);
    }
  }, [threadId]);

  const handleSendMessage = async (content) => {
    if (!threadId || !content.trim()) return;

    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    // Add placeholder assistant message for spatial consistency
    const placeholderId = `temp-${Date.now()}`;
    const placeholderAssistantMessage = {
      id: placeholderId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      agentSteps: {
        status: [],
        disambiguation: null,
        classification: null,
        extraction: null,
        tasks: [],
      },
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, placeholderAssistantMessage]);

    // Send message and handle streaming with placeholder ID
    await sendMessage(content, placeholderId);
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
                  <div className={`max-w-xs lg:max-w-md ${message.role === "user" ? "" : "w-full"}`}>
                    {/* Agent Steps Dropdown for assistant messages */}
                    {message.role === "assistant" && (
                      <AgentStepsDropdown
                        agentSteps={message.agentSteps}
                        isStreaming={message.isStreaming || (isStreaming && message === messages[messages.length - 1])}
                      />
                    )}

                    {/* Message Content */}
                    <div
                      className={`px-4 py-2 rounded-lg ${
                        message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"
                      }`}
                    >
                      <div className="text-sm font-medium mb-1">{message.role === "user" ? "You" : "Ableton Buddy"}</div>
                      <div className="text-sm">
                        {message.content ||
                          (message.isStreaming ? (
                            <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-500"></div>
                              <span>Thinking...</span>
                            </div>
                          ) : (
                            ""
                          ))}
                      </div>
                      {message.content && <div className="text-xs opacity-70 mt-1">{new Date(message.timestamp).toLocaleTimeString()}</div>}
                    </div>
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
