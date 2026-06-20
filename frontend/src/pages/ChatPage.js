import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Sparkles, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import Sidebar from '../components/chat/Sidebar';
import MessageBubble from '../components/chat/MessageBubble';
import VoiceRecorder from '../components/chat/VoiceRecorder';
import SentimentPanel from '../components/chat/SentimentPanel';
import { messagesAPI } from '../services/api';
import { Spinner } from '../components/ui';

export default function ChatPage() {
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [sentimentRefreshKey, setSentimentRefreshKey] = useState(0);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load message history when session changes
  useEffect(() => {
    if (!activeSession) return;
    setMessages([]);
    setLoadingHistory(true);
    messagesAPI.history(activeSession.id)
      .then(res => setMessages(res.data))
      .catch(() => toast.error('Could not load history'))
      .finally(() => setLoadingHistory(false));
  }, [activeSession]);

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInput(e.target.value);
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendText(); }
  };

  const sendText = useCallback(async () => {
    const text = input.trim();
    if (!text || !activeSession || sending) return;

    // Optimistic update
    const tempUserMsg = {
      id: `tmp-${Date.now()}`, role: 'user', content: text,
      input_type: 'text', created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setSending(true);

    try {
      const res = await messagesAPI.send(activeSession.id, text);
      const { response, sentiment, dominant_emotion } = res.data;

      // Replace temp with real + add AI reply
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempUserMsg.id),
        { ...tempUserMsg, sentiment, dominant_emotion },
        {
          id: `ai-${Date.now()}`, role: 'assistant', content: response,
          input_type: 'text', created_at: new Date().toISOString(),
        },
      ]);
      setSentimentRefreshKey(k => k + 1);
    } catch (err) {
      toast.error('Could not send message. Please try again.');
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id));
      setInput(text);
    } finally {
      setSending(false);
    }
  }, [input, activeSession, sending]);

  const sendVoice = useCallback(async (blob) => {
    if (!activeSession || sending) return;
    setSending(true);

    const tempMsg = {
      id: `tmp-voice-${Date.now()}`, role: 'user', content: '🎙 Processing voice…',
      input_type: 'voice', created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempMsg]);

    try {
      const res = await messagesAPI.sendVoice(activeSession.id, blob);
      const { transcription, response, sentiment, dominant_emotion } = res.data;

      setMessages(prev => [
        ...prev.filter(m => m.id !== tempMsg.id),
        {
          id: `voice-${Date.now()}`, role: 'user', content: transcription,
          input_type: 'voice', sentiment, dominant_emotion,
          transcription, created_at: new Date().toISOString(),
        },
        {
          id: `ai-voice-${Date.now()}`, role: 'assistant', content: response,
          input_type: 'text', created_at: new Date().toISOString(),
        },
      ]);
      setSentimentRefreshKey(k => k + 1);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Voice message failed. Please try again.';
      toast.error(detail);
      setMessages(prev => prev.filter(m => m.id !== tempMsg.id));
    } finally {
      setSending(false);
    }
  }, [activeSession, sending]);

  return (
    <div style={styles.shell}>
      <Sidebar
        activeSessionId={activeSession?.id}
        onSelectSession={setActiveSession}
        onNewSession={setActiveSession}
      />

      {/* Main column */}
      <main style={styles.main}>
        {!activeSession ? (
          <EmptyState />
        ) : (
          <>
            {/* Header */}
            <header style={styles.chatHeader}>
              <div style={styles.headerLeft}>
                <div style={styles.headerAvatar}><Sparkles size={14} color="#C4B5FD" /></div>
                <div>
                  <p style={styles.headerName}>Solace</p>
                  <p style={styles.headerSub}>AI Therapist · always here</p>
                </div>
              </div>
              <div style={styles.onlineDot} title="Online" />
            </header>

            {/* Messages */}
            <div style={styles.feed}>
              {loadingHistory && (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
                  <Spinner size={24} />
                </div>
              )}

              {!loadingHistory && messages.length === 0 && (
                <div style={styles.startPrompt}>
                  <p style={styles.startText}>
                    Start by sharing what's on your mind — or record a voice message below.
                  </p>
                </div>
              )}

              {messages.map(msg => (
                <MessageBubble key={msg.id} message={msg} />
              ))}

              {sending && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <div style={styles.typingAvatar}><span>✦</span></div>
                  <div style={styles.typingBubble}>
                    <span style={styles.typingDot} /><span style={styles.typingDot} /><span style={styles.typingDot} />
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div style={styles.inputBar}>
              <VoiceRecorder onSend={sendVoice} disabled={sending} />

              <div style={styles.textareaWrap}>
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Share what's on your mind…"
                  rows={1}
                  disabled={sending}
                  style={styles.textarea}
                />
              </div>

              <button
                onClick={sendText}
                disabled={!input.trim() || sending}
                style={{
                  ...styles.sendBtn,
                  opacity: (!input.trim() || sending) ? 0.4 : 1,
                  cursor: (!input.trim() || sending) ? 'not-allowed' : 'pointer',
                }}
                aria-label="Send message"
              >
                <Send size={16} color="#0D1117" />
              </button>
            </div>
          </>
        )}
      </main>

      {/* Sentiment panel */}
      <SentimentPanel key={sentimentRefreshKey} sessionId={activeSession?.id} />
    </div>
  );
}

function EmptyState() {
  return (
    <div style={styles.emptyState}>
      <div style={styles.emptyGlow} />
      <div style={styles.emptyIcon}><Sparkles size={28} color="#C4B5FD" /></div>
      <h2 style={styles.emptyHeading}>Your space to talk</h2>
      <p style={styles.emptySub}>
        Select a conversation from the sidebar,<br />or start a new one.
      </p>
      <div style={styles.features}>
        {[
          { icon: '💬', label: 'Text chat' },
          { icon: '🎙️', label: 'Voice messages' },
          { icon: '📊', label: 'Emotion insights' },
        ].map(f => (
          <div key={f.label} style={styles.featurePill}>
            <span>{f.icon}</span>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{f.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  shell: {
    display: 'flex', height: '100vh', overflow: 'hidden',
    background: 'var(--bg-base)',
  },
  main: {
    flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden',
    position: 'relative',
  },
  chatHeader: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '14px 24px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-card)',
    flexShrink: 0,
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  headerAvatar: {
    width: '36px', height: '36px', borderRadius: '50%',
    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  headerName: { fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' },
  headerSub: { fontSize: '11px', color: 'var(--text-muted)' },
  onlineDot: {
    width: '8px', height: '8px', borderRadius: '50%',
    background: 'var(--accent-teal)',
    boxShadow: '0 0 6px var(--accent-teal)',
  },
  feed: {
    flex: 1, overflowY: 'auto',
    padding: '28px 32px',
  },
  startPrompt: {
    display: 'flex', justifyContent: 'center', padding: '48px 0 32px',
  },
  startText: {
    fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.7,
  },
  typingAvatar: {
    width: '32px', height: '32px', borderRadius: '50%',
    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: 'var(--accent-primary)', fontSize: '16px', flexShrink: 0,
  },
  typingBubble: {
    display: 'flex', alignItems: 'center', gap: '5px',
    padding: '14px 18px',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderLeft: '3px solid var(--accent-primary)',
    borderRadius: 'var(--radius-lg)',
    borderBottomLeftRadius: '4px',
  },
  typingDot: {
    display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%',
    background: 'var(--accent-primary)', opacity: 0.7,
    animation: 'bounce 1.2s infinite',
  },
  inputBar: {
    display: 'flex', alignItems: 'flex-end', gap: '10px',
    padding: '14px 20px',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg-card)',
    flexShrink: 0,
  },
  textareaWrap: { flex: 1 },
  textarea: {
    width: '100%', resize: 'none', overflow: 'hidden',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    color: 'var(--text-primary)',
    fontSize: '14px', lineHeight: 1.6,
    padding: '10px 14px',
    fontFamily: 'var(--font-ui)',
    outline: 'none',
    transition: 'border-color 200ms',
    minHeight: '42px',
  },
  sendBtn: {
    width: '42px', height: '42px', borderRadius: 'var(--radius-md)', flexShrink: 0,
    background: 'var(--accent-primary)', border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'opacity 150ms, transform 100ms',
  },
  emptyState: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: '48px', position: 'relative', overflow: 'hidden',
  },
  emptyGlow: {
    position: 'absolute', top: '30%', left: '50%', transform: 'translate(-50%,-50%)',
    width: '400px', height: '400px', borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(196,181,253,0.06) 0%, transparent 70%)',
    pointerEvents: 'none',
  },
  emptyIcon: {
    width: '64px', height: '64px', borderRadius: '20px',
    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px',
  },
  emptyHeading: {
    fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)',
    letterSpacing: '-0.5px', marginBottom: '10px',
  },
  emptySub: {
    fontSize: '14px', color: 'var(--text-secondary)',
    textAlign: 'center', lineHeight: 1.7, marginBottom: '28px',
  },
  features: { display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center' },
  featurePill: {
    display: 'flex', alignItems: 'center', gap: '7px',
    padding: '8px 14px', borderRadius: '99px',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
  },
};
