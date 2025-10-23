import { MessageList as ChatScopeMessageList, Message } from "@chatscope/chat-ui-kit-react";
import { filterMessagesForDisplay } from "../../utils/messageFilter";

/**
 * Message list component using ChatScope
 */
export default function MessageList({ messages, showDetails }) {
  const filteredMessages = filterMessagesForDisplay(messages, showDetails);

  return (
    <ChatScopeMessageList>
      {filteredMessages.map((message) => (
        <Message
          key={message.id}
          model={{
            message: message.text,
            sentTime: message.timestamp,
            sender: message.sender,
            direction: message.direction,
            position: message.position,
          }}
        />
      ))}
    </ChatScopeMessageList>
  );
}
