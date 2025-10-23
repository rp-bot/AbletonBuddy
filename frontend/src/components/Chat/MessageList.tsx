/**
 * Chatscope-based message list with auto-scroll
 */

import { useEffect, useRef } from "react";
import { MainContainer, ChatContainer, MessageList as ChatscopeMessageList, Message, TypingIndicator } from "@chatscope/chat-ui-kit-react";
import type { MessageResponse } from "@/api/types";

interface MessageListProps {
  messages: MessageResponse[];
  status?: string;
}

export function MessageList({ messages, status }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  if (messages.length === 0 && !status) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <svg className="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
        <p className="text-lg font-medium">Start a Conversation</p>
        <p className="text-sm mt-2">Send a message to control Ableton Live with natural language</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <MainContainer className="h-full">
        <ChatContainer className="h-full">
          <ChatscopeMessageList className="h-full">
            {messages.map((message) => (
              <Message
                key={message.id}
                model={{
                  message: message.content,
                  sentTime: message.timestamp,
                  sender: message.role === "user" ? "You" : "Assistant",
                  direction: message.role === "user" ? "outgoing" : "incoming",
                  position: "single",
                }}
              />
            ))}
            {status && (
              <Message
                model={{
                  message: status,
                  sentTime: new Date().toISOString(),
                  sender: "Assistant",
                  direction: "incoming",
                  position: "single",
                }}
              >
                <TypingIndicator />
              </Message>
            )}
          </ChatscopeMessageList>
        </ChatContainer>
      </MainContainer>
      <div ref={bottomRef} />
    </div>
  );
}
