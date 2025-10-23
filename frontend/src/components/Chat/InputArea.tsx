/**
 * Chatscope-based message input area
 */

import { MessageInput } from "@chatscope/chat-ui-kit-react";

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export function InputArea({ onSendMessage, disabled }: InputAreaProps) {
  const handleSend = (_innerHtml: string, textContent: string, _innerText: string, _nodes: NodeList) => {
    if (textContent.trim() && !disabled) {
      onSendMessage(textContent);
    }
  };

  return (
    <div className="border-t border-gray-200">
      <MessageInput placeholder="Type a command for Ableton Live..." onSend={handleSend} disabled={disabled} attachButton={false} sendButton={true} />
    </div>
  );
}
