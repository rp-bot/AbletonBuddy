/**
 * Message filtering utilities for chat display
 */

/**
 * Check if a message is a cancelled message
 * @param {Object} message - Message object
 * @returns {boolean} True if message is cancelled
 */
function isCancelledMessage(message) {
  return message.content === "Generation stopped by user";
}

/**
 * Filter messages to show user, assistant, and cancelled messages
 * @param {Array} messages - Array of message objects from API
 * @returns {Array} Filtered messages
 */
export function filterMessagesForDisplay(messages) {
  if (!messages || !Array.isArray(messages)) {
    return [];
  }

  // Filter to show user, assistant, and cancelled messages
  return messages.filter((message) => message.role === "user" || message.role === "assistant" || isCancelledMessage(message)).map(transformMessage);
}

/**
 * Transform API message format to ChatScope format
 * @param {Object} message - Message from API
 * @returns {Object} Transformed message for ChatScope
 */
function transformMessage(message) {
  return {
    id: message.id,
    type: message.role === "user" ? "text" : "text",
    direction: message.role === "user" ? "outgoing" : "incoming",
    position: "normal",
    text: message.content,
    timestamp: new Date(message.timestamp),
    sender: message.role === "user" ? "You" : "Ableton Buddy",
    // Store original message for detailed view
    originalMessage: message,
  };
}

/**
 * Get message count for a thread
 * @param {Array} messages - Array of message objects
 * @returns {number} Count of user, assistant, and cancelled messages
 */
export function getDisplayMessageCount(messages) {
  if (!messages || !Array.isArray(messages)) {
    return 0;
  }

  return messages.filter((message) => message.role === "user" || message.role === "assistant" || isCancelledMessage(message)).length;
}

/**
 * Get thread preview text from first user message
 * @param {Array} messages - Array of message objects
 * @returns {string} Preview text
 */
export function getThreadPreview(messages) {
  if (!messages || !Array.isArray(messages)) {
    return "No messages";
  }

  const firstUserMessage = messages.find((message) => message.role === "user");
  if (firstUserMessage) {
    return firstUserMessage.content.length > 50 ? firstUserMessage.content.substring(0, 50) + "..." : firstUserMessage.content;
  }

  return "No user messages";
}
