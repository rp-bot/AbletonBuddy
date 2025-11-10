import { useState } from "react";
import { MessageInput } from "@chatscope/chat-ui-kit-react";
import { useVoiceRecorder } from "../../hooks/useVoiceRecorder";
import MicrophoneButton from "./MicrophoneButton";

/**
 * Input area component for sending messages
 */
export default function InputArea({ onSendMessage, isStreaming, disabled }) {
  const [message, setMessage] = useState("");

  const handleTranscript = (transcript) => {
    // Append transcript to existing message or set as new message
    setMessage((prev) => {
      const trimmed = prev.trim();
      return trimmed ? `${trimmed} ${transcript}` : transcript;
    });
  };

  const {
    isRecording,
    isProcessing,
    error: recordingError,
    startRecording,
    stopRecording,
    toggleRecording,
  } = useVoiceRecorder(handleTranscript);

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

  const isVoiceDisabled = disabled || isStreaming;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-end space-x-2">
        <div className="relative flex-1">
          <MessageInput
            placeholder={isStreaming ? "Processing..." : "Type your message..."}
            value={message}
            onChange={(val) => setMessage(val)}
            onKeyPress={handleKeyPress}
            disabled={disabled || isStreaming}
            attachButton={false}
            sendButton={false}
            style={{ paddingRight: "80px" }}
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1 items-center z-10">
            <MicrophoneButton
              mode="hold"
              isRecording={isRecording}
              isProcessing={isProcessing}
              onStart={() => startRecording("hold")}
              onStop={stopRecording}
              disabled={isVoiceDisabled}
            />
            <MicrophoneButton
              mode="toggle"
              isRecording={isRecording}
              isProcessing={isProcessing}
              onToggle={toggleRecording}
              disabled={isVoiceDisabled}
            />
          </div>
        </div>
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled || isStreaming}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors"
        >
          {isStreaming ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : "Send"}
        </button>
      </div>
      {recordingError && (
        <div className="mt-2 text-sm text-red-600 dark:text-red-400">{recordingError}</div>
      )}
    </div>
  );
}
