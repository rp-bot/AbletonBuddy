import { FaUser, FaRobot } from "react-icons/fa";

/**
 * Avatar component for chat messages
 * @param {string} role - "user" or "assistant"
 * @param {string} size - "sm", "md", or "lg" (default: "md")
 */
export default function Avatar({ role, size = "md" }) {
  const sizeClasses = {
    sm: "w-6 h-6 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-10 h-10 text-base",
  };

  const iconSize = {
    sm: 12,
    md: 16,
    lg: 20,
  };

  const isUser = role === "user";
  const Icon = isUser ? FaUser : FaRobot;
  const bgColor = isUser ? "bg-blue-500" : "bg-purple-500";

  const iconColor = "text-white";

  return (
    <div className={`${sizeClasses[size]} ${bgColor} ${iconColor} rounded-full flex items-center justify-center shrink-0`}>
      <Icon size={iconSize[size]} />
    </div>
  );
}
