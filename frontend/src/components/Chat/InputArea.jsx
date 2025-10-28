import { useState } from "react";
import { MessageInput } from "@chatscope/chat-ui-kit-react";

/**
 * Input area component for sending messages
 */
export default function InputArea({ onSendMessage, isStreaming, disabled }) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled && !isStreaming) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <MessageInput
            placeholder={isStreaming ? "Processing..." : "Type your message..."}
            value={message}
            onChange={(val) => setMessage(val)}
            onKeyPress={handleKeyPress}
            disabled={disabled || isStreaming}
            attachButton={false}
            sendButton={false}
          />
        </div>
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled || isStreaming}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors"
        >
          {isStreaming ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : "Send"}
        </button>
      </div>
    </div>
  );
}
