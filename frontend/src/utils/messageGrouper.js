/**
 * Message grouping utilities for chat display
 * Groups agent processing steps with their corresponding assistant messages
 */

/**
 * Group messages by conversation turn and associate agent steps with assistant messages
 * @param {Array} messages - Array of detailed message objects from API
 * @returns {Array} Grouped messages with agent steps attached
 */
export function groupMessagesWithAgentSteps(messages) {
  if (!messages || !Array.isArray(messages)) {
    return [];
  }

  // console.log("groupMessagesWithAgentSteps - input messages:", messages);
  const groupedMessages = [];
  let currentAgentSteps = [];
  let lastUserMessage = null;

  for (let i = 0; i < messages.length; i++) {
    const message = messages[i];
    const role = message.role;

    if (role === "user") {
      // Save any accumulated agent steps to the previous assistant message
      if (lastUserMessage && groupedMessages.length > 0) {
        const lastAssistantIndex = groupedMessages.length - 1;
        if (groupedMessages[lastAssistantIndex].role === "assistant") {
          groupedMessages[lastAssistantIndex].agentSteps = parseAgentSteps(currentAgentSteps);
        }
      }

      // Start new conversation turn
      lastUserMessage = message;
      currentAgentSteps = [];
      groupedMessages.push({
        ...message,
        agentSteps: null,
      });
    } else if (role === "assistant" || role === "clarification") {
      // This is the final summarization message - attach current agent steps
      const parsedSteps = parseAgentSteps(currentAgentSteps);

      // Clean the content by removing "Summarization Agent:" prefix (like backend does)
      const cleanContent =
        role === "assistant"
          ? message.content.replace("Summarization Agent:", "").trim()
          : message.content.replace("Clarification Agent:", "").trim();

      // console.log("Assistant message - currentAgentSteps:", currentAgentSteps);
      // console.log("Assistant message - parsedSteps:", parsedSteps);
      groupedMessages.push({
        ...message,
        role: "assistant",
        messageType: role,
        content: cleanContent,
        agentSteps: parsedSteps,
      });
      // Clear agent steps for next conversation turn
      currentAgentSteps = [];
    } else if (isAgentStepRole(role)) {
      // This is an agent processing step
      // console.log("Agent step found:", role, message);
      currentAgentSteps.push(message);
    }
  }

  // Attach any remaining agent steps to the last assistant message
  if (currentAgentSteps.length > 0 && groupedMessages.length > 0) {
    const lastMessage = groupedMessages[groupedMessages.length - 1];
    if (lastMessage.role === "assistant") {
      lastMessage.agentSteps = parseAgentSteps(currentAgentSteps);
    }
  }

  return groupedMessages;
}

/**
 * Check if a role represents an agent processing step
 * @param {string} role - Message role
 * @returns {boolean} True if it's an agent step
 */
function isAgentStepRole(role) {
  const isAgentStep = ["status", "disambiguation", "classification", "extraction", "task_success", "task_failed", "task_skipped", "task_created"].includes(
    role,
  );
  // console.log(`isAgentStepRole(${role}): ${isAgentStep}`);
  return isAgentStep;
}

/**
 * Parse agent steps into structured format
 * @param {Array} agentStepMessages - Array of agent step messages
 * @returns {Object} Structured agent steps
 */
function parseAgentSteps(agentStepMessages) {
  const agentSteps = {
    status: [],
    disambiguation: null,
    classification: null,
    extraction: null,
    tasks: [],
  };

  for (const message of agentStepMessages) {
    const { role, content, timestamp } = message;

    switch (role) {
      case "status":
        agentSteps.status.push({
          data: content,
          timestamp: timestamp,
        });
        break;

      case "disambiguation":
        agentSteps.disambiguation = {
          data: content,
          timestamp: timestamp,
        };
        break;

      case "classification":
        agentSteps.classification = {
          data: content,
          timestamp: timestamp,
        };
        break;

      case "extraction":
        agentSteps.extraction = {
          data: content,
          timestamp: timestamp,
        };
        break;

      case "task_success":
      case "task_failed":
      case "task_skipped":
        const task = parseTaskMessage(content, role, timestamp);
        if (task) {
          agentSteps.tasks.push(task);
        }
        break;
    }
  }

  return agentSteps;
}

/**
 * Parse task message content to extract task details
 * @param {string} content - Task message content
 * @param {string} role - Task role (task_success, task_failed, task_skipped)
 * @param {string} timestamp - Message timestamp
 * @returns {Object|null} Parsed task object
 */
function parseTaskMessage(content, role, timestamp) {
  try {
    // Extract task details from content
    // Format: "Task Successful:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
    const lines = content.split("\n").filter((line) => line.trim());

    if (lines.length < 3) return null;

    const taskId = lines[1]?.replace("-", "").trim();
    const taskName = lines[2]?.replace("-", "").trim();
    const taskResult = lines[3]?.replace("-", "").trim();
    const taskTools = lines[4]?.replace("-", "").trim() || "";

    return {
      id: taskId,
      name: taskName,
      status: role.replace("task_", ""),
      result: taskResult,
      tools: taskTools ? taskTools.split(",").map((t) => t.trim()) : [],
      timestamp: timestamp,
    };
  } catch (error) {
    console.warn("Failed to parse task message:", content, error);
    return null;
  }
}

/**
 * Get a summary of agent steps for display
 * @param {Object} agentSteps - Parsed agent steps object
 * @returns {string} Summary text
 */
export function getAgentStepsSummary(agentSteps) {
  if (!agentSteps) return "No processing steps";

  const stepCount =
    (agentSteps.status?.length || 0) +
    (agentSteps.disambiguation ? 1 : 0) +
    (agentSteps.classification ? 1 : 0) +
    (agentSteps.extraction ? 1 : 0) +
    (agentSteps.tasks?.length || 0);

  if (stepCount === 0) return "No processing steps";

  return `Processed through ${stepCount} step${stepCount !== 1 ? "s" : ""}`;
}

/**
 * Check if agent steps are currently being processed (for streaming state)
 * @param {Object} agentSteps - Parsed agent steps object
 * @param {string} messageContent - The message content to check for cancellation
 * @returns {boolean} True if still processing
 */
export function isAgentStepsProcessing(agentSteps, messageContent = "", messageType = "assistant") {
  if (!agentSteps) return true;

  // If message is cancelled, it's not processing
  const isCancelled = messageContent === "Generation stopped by user";
  if (isCancelled) return false;

  if (messageType === "clarification" || messageContent.startsWith("I need more information to help you")) {
    return false;
  }

  // If we have status messages but no final tasks, we're still processing
  const hasStatus = agentSteps.status && agentSteps.status.length > 0;
  const hasTasks = agentSteps.tasks && agentSteps.tasks.length > 0;

  return hasStatus && !hasTasks;
}
