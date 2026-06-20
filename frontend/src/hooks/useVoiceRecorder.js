import { useState, useRef, useCallback } from "react";

export function useVoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null); // keep stream ref to kill tracks reliably
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const mimeTypeRef = useRef("audio/webm");

  /** Tear down any existing recorder/stream completely */
  const _cleanup = useCallback(() => {
    clearInterval(timerRef.current);
    if (mediaRecorderRef.current) {
      try {
        if (mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop();
        }
      } catch {}
      mediaRecorderRef.current.ondataavailable = null;
      mediaRecorderRef.current.onstop = null;
      mediaRecorderRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const startRecording = useCallback(async () => {
    // Always clean up before starting fresh
    _cleanup();
    chunksRef.current = [];
    setError(null);
    setAudioBlob(null);
    setDuration(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });
      streamRef.current = stream;

      // Pick best supported mime type
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")
            ? "audio/ogg;codecs=opus"
            : MediaRecorder.isTypeSupported("audio/mp4")
              ? "audio/mp4"
              : "";

      mimeTypeRef.current = mimeType || "audio/webm";

      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const chunks = chunksRef.current;
        if (chunks.length === 0) return; // nothing was captured
        const blob = new Blob(chunks, { type: mimeTypeRef.current });
        setAudioBlob(blob);
        // Release mic
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
      };

      recorder.start(250); // chunk every 250ms — more reliable than 100ms
      mediaRecorderRef.current = recorder;
      setIsRecording(true);

      // Duration timer
      const start = Date.now();
      timerRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - start) / 1000));
      }, 500);
    } catch (err) {
      _cleanup();
      if (
        err.name === "NotAllowedError" ||
        err.name === "PermissionDeniedError"
      ) {
        setError(
          "Microphone access denied. Allow mic access in browser settings.",
        );
      } else {
        setError("Could not access microphone: " + err.message);
      }
    }
  }, [_cleanup]);

  const stopRecording = useCallback(() => {
    clearInterval(timerRef.current);
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop(); // triggers onstop → sets audioBlob
    }
    setIsRecording(false);
  }, []);

  const clearRecording = useCallback(() => {
    _cleanup();
    chunksRef.current = [];
    setAudioBlob(null);
    setDuration(0);
    setError(null);
  }, [_cleanup]);

  /** Returns the right filename extension for Groq/Whisper */
  const getFilename = useCallback(() => {
    const mime = mimeTypeRef.current;
    if (mime.includes("ogg")) return "recording.ogg";
    if (mime.includes("mp4")) return "recording.mp4";
    return "recording.webm"; // default
  }, []);

  return {
    isRecording,
    audioBlob,
    duration,
    error,
    startRecording,
    stopRecording,
    clearRecording,
    getFilename,
  };
}
