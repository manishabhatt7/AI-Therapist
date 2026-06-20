import React, { useEffect, useRef } from "react";
import { Mic, Square, Trash2, Send, Upload } from "lucide-react";
import { useVoiceRecorder } from "../../hooks/useVoiceRecorder";
import { formatDuration } from "../../utils/helpers";
import { Tooltip } from "../ui";

const ACCEPTED =
  "audio/webm,audio/mp4,audio/ogg,audio/mpeg,audio/wav,audio/m4a,.webm,.mp4,.ogg,.mp3,.wav,.m4a";

export default function VoiceRecorder({ onSend, disabled }) {
  const {
    isRecording,
    audioBlob,
    duration,
    error,
    startRecording,
    stopRecording,
    clearRecording,
    getFilename,
  } = useVoiceRecorder();

  const barsRef = useRef([]);
  const fileInputRef = useRef(null);

  // Animate waveform bars
  useEffect(() => {
    if (!isRecording) {
      barsRef.current.forEach((b) => {
        if (b) b.style.height = "4px";
      });
      return;
    }
    const interval = setInterval(() => {
      barsRef.current.forEach((b) => {
        if (b) b.style.height = `${4 + Math.random() * 20}px`;
      });
    }, 120);
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleSend = () => {
    if (audioBlob) {
      onSend(audioBlob, getFilename());
      clearRecording();
    }
  };

  // File upload handler
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = ""; // reset so same file can be re-selected
    onSend(file, file.name);
  };

  return (
    <div style={styles.wrapper}>
      {error && <p style={styles.error}>{error}</p>}

      {/* Idle: mic + upload */}
      {!isRecording && !audioBlob && (
        <div style={{ display: "flex", gap: "6px" }}>
          <Tooltip text="Record voice message">
            <button
              onClick={startRecording}
              disabled={disabled}
              style={{
                ...styles.iconBtn,
                opacity: disabled ? 0.4 : 1,
                cursor: disabled ? "not-allowed" : "pointer",
              }}
              aria-label="Start recording"
            >
              <Mic size={17} color="var(--text-secondary)" />
            </button>
          </Tooltip>

          <Tooltip text="Upload audio file">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled}
              style={{
                ...styles.iconBtn,
                opacity: disabled ? 0.4 : 1,
                cursor: disabled ? "not-allowed" : "pointer",
              }}
              aria-label="Upload audio file"
            >
              <Upload size={17} color="var(--text-secondary)" />
            </button>
          </Tooltip>

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED}
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
        </div>
      )}

      {/* Recording */}
      {isRecording && (
        <div style={styles.recording}>
          <div style={styles.waveform}>
            {Array.from({ length: 12 }).map((_, i) => (
              <span
                key={i}
                ref={(el) => (barsRef.current[i] = el)}
                style={{
                  ...styles.bar,
                  background:
                    i % 2 === 0
                      ? "var(--accent-primary)"
                      : "var(--accent-primary)80",
                }}
              />
            ))}
          </div>
          <span style={styles.timer}>{formatDuration(duration)}</span>
          <button
            onClick={stopRecording}
            style={styles.stopBtn}
            aria-label="Stop recording"
          >
            <Square size={14} fill="white" color="white" />
          </button>
        </div>
      )}

      {/* Preview: recorded blob ready */}
      {audioBlob && !isRecording && (
        <div style={styles.preview}>
          <div style={styles.previewIcon}>
            <Mic size={14} color="var(--accent-primary)" />
          </div>
          <span style={styles.previewLabel}>
            {formatDuration(duration)} voice
          </span>
          <audio
            src={URL.createObjectURL(audioBlob)}
            controls
            style={{ height: "28px", flex: 1, maxWidth: "140px" }}
          />
          <Tooltip text="Discard">
            <button
              onClick={clearRecording}
              style={styles.actionBtn}
              aria-label="Discard"
            >
              <Trash2 size={15} color="var(--accent-rose)" />
            </button>
          </Tooltip>
          <Tooltip text="Send">
            <button
              onClick={handleSend}
              style={{ ...styles.actionBtn, ...styles.sendBtn }}
              aria-label="Send voice message"
            >
              <Send size={15} color="white" />
            </button>
          </Tooltip>
        </div>
      )}
    </div>
  );
}

const styles = {
  wrapper: { display: "flex", alignItems: "center", gap: "6px" },
  error: { fontSize: "11px", color: "var(--accent-rose)", maxWidth: "200px" },
  iconBtn: {
    width: "38px",
    height: "38px",
    background: "var(--bg-elevated)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-md)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 150ms, border-color 150ms",
    flexShrink: 0,
  },
  recording: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: "rgba(196,181,253,0.08)",
    border: "1px solid var(--border-accent)",
    borderRadius: "var(--radius-lg)",
    padding: "6px 12px",
  },
  waveform: {
    display: "flex",
    alignItems: "center",
    gap: "3px",
    height: "28px",
  },
  bar: {
    width: "3px",
    borderRadius: "2px",
    height: "4px",
    transition: "height 120ms ease",
    display: "inline-block",
  },
  timer: {
    fontSize: "12px",
    fontWeight: 600,
    color: "var(--accent-primary)",
    fontVariantNumeric: "tabular-nums",
    minWidth: "36px",
  },
  stopBtn: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    background: "var(--accent-rose)",
    border: "none",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  preview: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "var(--bg-elevated)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: "6px 10px",
  },
  previewIcon: {
    width: "26px",
    height: "26px",
    background: "var(--accent-glow)",
    border: "1px solid var(--border-accent)",
    borderRadius: "var(--radius-sm)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  previewLabel: {
    fontSize: "12px",
    color: "var(--text-secondary)",
    whiteSpace: "nowrap",
  },
  actionBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: "4px",
    borderRadius: "var(--radius-sm)",
    display: "flex",
    alignItems: "center",
  },
  sendBtn: {
    background: "var(--accent-primary)",
    padding: "6px 10px",
    borderRadius: "var(--radius-md)",
  },
};
