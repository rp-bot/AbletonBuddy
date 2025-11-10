import { useState, useRef, useCallback } from "react";
import { transcribeAudio } from "../api/client";

/**
 * Custom hook for voice recording with dual modes (hold and toggle)
 * @param {Function} onTranscript - Callback when transcription is complete
 * @returns {Object} Recording controls and state
 */
export function useVoiceRecorder(onTranscript) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const isToggleModeRef = useRef(false);

  /**
   * Request microphone access and initialize MediaRecorder
   */
  const initializeRecorder = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4",
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks to release microphone
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }

        // Process audio if we have chunks
        if (audioChunksRef.current.length > 0) {
          setIsProcessing(true);
          setError(null);

          try {
            const audioBlob = new Blob(audioChunksRef.current, {
              type: mediaRecorder.mimeType,
            });

            // Transcribe audio
            const transcript = await transcribeAudio(audioBlob);

            if (transcript && onTranscript) {
              onTranscript(transcript);
            }
          } catch (err) {
            console.error("Transcription error:", err);
            setError(err.message || "Failed to transcribe audio");
          } finally {
            setIsProcessing(false);
            audioChunksRef.current = [];
          }
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      return true;
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError(
        err.name === "NotAllowedError"
          ? "Microphone permission denied"
          : err.name === "NotFoundError"
            ? "No microphone found"
            : "Failed to access microphone"
      );
      return false;
    }
  }, [onTranscript]);

  /**
   * Start recording
   * @param {string} mode - "hold" or "toggle"
   */
  const startRecording = useCallback(
    async (mode) => {
      if (isRecording || isProcessing) return;

      isToggleModeRef.current = mode === "toggle";

      const initialized = await initializeRecorder();
      if (!initialized) return;

      try {
        audioChunksRef.current = [];
        mediaRecorderRef.current.start();
        setIsRecording(true);
        setError(null);
      } catch (err) {
        console.error("Error starting recording:", err);
        setError("Failed to start recording");
      }
    },
    [isRecording, isProcessing, initializeRecorder]
  );

  /**
   * Stop recording
   */
  const stopRecording = useCallback(() => {
    if (!isRecording || !mediaRecorderRef.current) return;

    try {
      if (mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } catch (err) {
      console.error("Error stopping recording:", err);
      setError("Failed to stop recording");
      setIsRecording(false);
    }
  }, [isRecording]);

  /**
   * Toggle recording (for toggle mode)
   */
  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording("toggle");
    }
  }, [isRecording, startRecording, stopRecording]);

  /**
   * Cancel recording (clean up without processing)
   */
  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }

    // Stop all tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    audioChunksRef.current = [];
    setIsRecording(false);
    setIsProcessing(false);
    setError(null);
  }, []);

  return {
    isRecording,
    isProcessing,
    error,
    startRecording,
    stopRecording,
    toggleRecording,
    cancelRecording,
  };
}

