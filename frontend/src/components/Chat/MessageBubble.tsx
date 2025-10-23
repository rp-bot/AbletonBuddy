/**
 * Individual message bubble component
 */

import type { MessageResponse } from "@/api/types";

interface MessageBubbleProps {
  message: MessageResponse;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const formattedTime = new Date(message.timestamp).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[70%] rounded-lg px-4 py-2 ${isUser ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-800"}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold">{isUser ? "You" : "Assistant"}</span>
          <span className="text-xs opacity-75">{formattedTime}</span>
        </div>
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}
