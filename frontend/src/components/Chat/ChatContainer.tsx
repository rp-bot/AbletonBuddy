/**
 * Main chat container with messages and input
 */

import { useEffect, useState } from "react";
import { MessageList } from "./MessageList";
import { InputArea } from "./InputArea";
import { useMessages, useInvalidateMessages } from "@/hooks/useMessages";
import { useStreamingChat } from "@/hooks/useStreamingChat";
import type { MessageResponse } from "@/api/types";

interface ChatContainerProps {
  threadId: string | null;
}

export function ChatContainer({ threadId }: ChatContainerProps) {
  const { data: threadData, isLoading } = useMessages(threadId);
  const invalidateMessages = useInvalidateMessages();
  const { sendMessage, isStreaming, currentStatus } = useStreamingChat();

  // Local state for optimistic updates
  const [localMessages, setLocalMessages] = useState<MessageResponse[]>([]);

  // Update local messages when thread data changes
  useEffect(() => {
    if (threadData?.messages) {
      setLocalMessages(threadData.messages);
    } else {
      setLocalMessages([]);
    }
  }, [threadData]);

  const handleSendMessage = async (content: string) => {
    if (!threadId) return;

    // Optimistically add user message
    const optimisticMessage: MessageResponse = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setLocalMessages((prev) => [...prev, optimisticMessage]);

    // Send message with streaming
    await sendMessage(
      threadId,
      { content },
      {
        onStatus: (status) => {
          console.log("Status:", status);
        },
        onMessage: (message) => {
          // Add assistant message
          const assistantMessage: MessageResponse = {
            id: `response-${Date.now()}`,
            role: "assistant",
            content: message,
            timestamp: new Date().toISOString(),
          };
          setLocalMessages((prev) => [...prev, assistantMessage]);

          // Refresh from server to get accurate data
          invalidateMessages(threadId);
        },
        onDone: () => {
          console.log("Stream complete");
          // Final refresh to ensure consistency
          invalidateMessages(threadId);
        },
        onError: (error) => {
          console.error("Stream error:", error);
          // Optionally show error message
          const errorMessage: MessageResponse = {
            id: `error-${Date.now()}`,
            role: "assistant",
            content: `Error: ${error}`,
            timestamp: new Date().toISOString(),
          };
          setLocalMessages((prev) => [...prev, errorMessage]);
        },
      },
    );
  };

  if (!threadId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <svg className="w-20 h-20 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <p className="text-lg font-medium">No Conversation Selected</p>
          <p className="text-sm mt-2">Select a thread or create a new one to get started</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading messages...</div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50 h-full">
      <div className="flex-1 overflow-hidden">
        <MessageList messages={localMessages} status={currentStatus} />
      </div>
      <InputArea onSendMessage={handleSendMessage} disabled={isStreaming} />
    </div>
  );
}
