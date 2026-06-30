import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Mic, ChevronDown, ChevronUp } from 'lucide-react';
import { formatTime, getEmotionMeta } from '../../utils/helpers';
import AudioPlayer from './AudioPlayer';

export default function MessageBubble({ message }) {
  const isUser  = message.role === 'user';
  const isVoice = message.input_type === 'voice';
  const meta    = message.dominant_emotion ? getEmotionMeta(message.dominant_emotion) : null;
  const [showTranscript, setShowTranscript] = useState(false);

  return (
    <div style={{
      display:       'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems:    'flex-end',
      gap:           '10px',
      marginBottom:  '20px',
    }}>
      {!isUser && <div style={styles.aiAvatar}>✦</div>}

      <div style={{
        display:       'flex',
        flexDirection: 'column',
        maxWidth:      '72%',
        alignItems:    isUser ? 'flex-end' : 'flex-start',
        gap:           '4px',
      }}>
        <div style={{ ...styles.bubble, ...(isUser ? styles.userBubble : styles.aiBubble) }}>

          {isUser && isVoice && (
            <div style={styles.voiceTag}>
              <Mic size={11} color="var(--accent-primary)" />
              <span style={{ fontSize: '11px', color: 'var(--accent-primary)', fontWeight: 500 }}>
                Voice message
              </span>
            </div>
          )}

          {isUser ? (
            <p style={styles.userText}>{message.content}</p>
          ) : (
            <div style={styles.aiText}>
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p style={{ marginBottom: '10px' }}>{children}</p>,
                  strong: ({ children }) => (
                    <strong style={{ color: 'var(--text-primary)' }}>{children}</strong>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>

              {/* Audio player — pass both base64 and MIME type */}
              {message.audio_base64 && (
                <AudioPlayer
                  base64audio={message.audio_base64}
                  mimeType={message.audio_mime || 'audio/wav'}
                  autoPlay
                />
              )}
            </div>
          )}

          {isUser && isVoice && message.transcription && (
            <button onClick={() => setShowTranscript(v => !v)} style={styles.transcriptToggle}>
              {showTranscript ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              <span style={{ fontSize: '11px' }}>
                {showTranscript ? 'Hide transcript' : 'Show transcript'}
              </span>
            </button>
          )}
          {showTranscript && (
            <p style={styles.transcript}>"{message.transcription}"</p>
          )}
        </div>

        <div style={{
          display:       'flex',
          alignItems:    'center',
          gap:           '8px',
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}>
          <span style={styles.timestamp}>{formatTime(message.created_at)}</span>
          {meta && isUser && (
            <span style={{
              fontSize:     '11px',
              color:        meta.color,
              background:   `${meta.color}15`,
              padding:      '2px 7px',
              borderRadius: '99px',
              border:       `1px solid ${meta.color}25`,
              display:      'flex',
              alignItems:   'center',
              gap:          '4px',
            }}>
              {meta.emoji} {meta.label}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  aiAvatar: {
    width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: 'var(--accent-primary)', fontSize: '16px',
  },
  bubble: {
    padding: '14px 18px', borderRadius: 'var(--radius-lg)', wordBreak: 'break-word',
  },
  userBubble: {
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    borderBottomRightRadius: '4px',
  },
  aiBubble: {
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderLeft: '3px solid var(--accent-primary)',
    boxShadow: '-4px 0 20px rgba(196,181,253,0.06)',
    borderBottomLeftRadius: '4px',
  },
  userText: {
    fontSize: '14px', color: 'var(--text-primary)',
    lineHeight: 1.65, fontFamily: 'var(--font-ui)',
  },
  aiText: {
    fontSize: '15px', color: 'var(--text-secondary)',
    lineHeight: 1.75, fontFamily: 'var(--font-content)',
  },
  voiceTag:         { display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' },
  transcriptToggle: {
    display: 'flex', alignItems: 'center', gap: '4px',
    background: 'none', border: 'none', cursor: 'pointer',
    color: 'var(--text-muted)', marginTop: '8px', padding: 0,
  },
  transcript: {
    fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic',
    marginTop: '6px', padding: '8px', background: 'var(--bg-base)',
    borderRadius: 'var(--radius-sm)', lineHeight: 1.5,
  },
  timestamp: { fontSize: '11px', color: 'var(--text-muted)' },
};