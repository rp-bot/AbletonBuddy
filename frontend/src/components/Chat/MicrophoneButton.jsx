import { FaMicrophone, FaMicrophoneSlash } from "react-icons/fa";

/**
 * Microphone button component with support for hold and toggle modes
 * @param {string} mode - "hold" or "toggle"
 * @param {boolean} isRecording - Whether currently recording
 * @param {boolean} isProcessing - Whether processing transcription
 * @param {Function} onStart - Callback when recording starts
 * @param {Function} onStop - Callback when recording stops
 * @param {Function} onToggle - Callback for toggle mode
 * @param {boolean} disabled - Whether button is disabled
 * @param {string} className - Additional CSS classes
 */
export default function MicrophoneButton({
  mode,
  isRecording,
  isProcessing,
  onStart,
  onStop,
  onToggle,
  disabled = false,
  className = "",
}) {
  const handleMouseDown = (e) => {
    if (mode === "hold" && !disabled && !isProcessing) {
      e.preventDefault();
      onStart?.();
    }
  };

  const handleMouseUp = (e) => {
    if (mode === "hold" && !disabled) {
      e.preventDefault();
      onStop?.();
    }
  };

  const handleMouseLeave = (e) => {
    if (mode === "hold" && isRecording && !disabled) {
      e.preventDefault();
      onStop?.();
    }
  };

  const handleClick = (e) => {
    if (mode === "toggle" && !disabled && !isProcessing) {
      e.preventDefault();
      onToggle?.();
    }
  };

  const getIcon = () => {
    if (isProcessing) {
      return (
        <div className="relative w-4 h-4">
          <div className="animate-spin rounded-full w-4 h-4 border-2 border-gray-300 border-t-gray-600 dark:border-gray-600 dark:border-t-gray-300"></div>
        </div>
      );
    }
    if (isRecording) {
      return <FaMicrophone className="w-4 h-4" />;
    }
    return <FaMicrophoneSlash className="w-4 h-4" />;
  };

  const isActive = isRecording || isProcessing;

  return (
    <button
      type="button"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      disabled={disabled || isProcessing}
      className={`
        relative flex items-center justify-center
        w-8 h-8 rounded-full
        transition-all duration-200
        ${isActive ? "bg-red-500 hover:bg-red-600" : "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"}
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        ${isRecording ? "animate-pulse" : ""}
        ${className}
      `}
      title={
        mode === "hold"
          ? isRecording
            ? "Release to stop recording"
            : "Hold to record"
          : isRecording
            ? "Click to stop recording"
            : "Click to start recording"
      }
    >
      <div className={isActive ? "text-white" : "text-gray-600 dark:text-gray-300"}>
        {getIcon()}
      </div>
      {isRecording && (
        <span className="absolute inset-0 w-3 h-3 m-auto bg-red-600 rounded-full animate-ping"></span>
      )}
    </button>
  );
}

