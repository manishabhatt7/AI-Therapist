import React, { useState, useEffect, useCallback } from 'react';
import { BarChart2, RefreshCw, AlertTriangle, TrendingUp, Mic, MessageSquare } from 'lucide-react';
import { messagesAPI } from '../../services/api';
import { getEmotionMeta, sentimentColor } from '../../utils/helpers';
import { Spinner } from '../ui';

export default function SentimentPanel({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await messagesAPI.sentimentSummary(sessionId);
      setData(res.data);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => { load(); }, [load]);

  if (!sessionId) return null;

  return (
    <aside style={styles.panel}>
      <div style={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart2 size={15} color="var(--accent-primary)" />
          <span style={styles.headerTitle}>Session Insights</span>
        </div>
        <button onClick={load} style={styles.refreshBtn} aria-label="Refresh insights">
          <RefreshCw size={14} color="var(--text-muted)" />
        </button>
      </div>

      <div style={styles.body}>
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '32px 0' }}>
            <Spinner />
          </div>
        )}

        {!loading && !data && (
          <div style={styles.empty}>
            <TrendingUp size={28} color="var(--text-muted)" />
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.5 }}>
              Insights appear after your first message.
            </p>
          </div>
        )}

        {!loading && data && data.message && (
          <div style={styles.empty}>
            <TrendingUp size={28} color="var(--text-muted)" />
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center' }}>
              {data.message}
            </p>
          </div>
        )}

        {!loading && data && !data.message && (
          <>
            {/* Dominant emotion */}
            {data.dominant_emotion_overall && (() => {
              const meta = getEmotionMeta(data.dominant_emotion_overall);
              return (
                <div style={styles.card}>
                  <p style={styles.cardLabel}>Primary emotion</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '8px' }}>
                    <span style={{ fontSize: '28px' }}>{meta.emoji}</span>
                    <div>
                      <p style={{ fontSize: '16px', fontWeight: 600, color: meta.color }}>
                        {meta.label}
                      </p>
                      {data.average_confidence && (
                        <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          {Math.round(data.average_confidence * 100)}% confidence
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* Input breakdown */}
            <div style={styles.card}>
              <p style={styles.cardLabel}>Message types</p>
              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                <div style={styles.statPill}>
                  <MessageSquare size={12} color="var(--accent-primary)" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {data.text_message_count ?? 0}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>text</span>
                </div>
                <div style={styles.statPill}>
                  <Mic size={12} color="var(--accent-teal)" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {data.voice_message_count ?? 0}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>voice</span>
                </div>
              </div>
            </div>

            {/* Sentiment breakdown */}
            {data.sentiment_breakdown && Object.keys(data.sentiment_breakdown).length > 0 && (
              <div style={styles.card}>
                <p style={styles.cardLabel}>Sentiment</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '10px' }}>
                  {Object.entries(data.sentiment_breakdown)
                    .sort(([, a], [, b]) => b - a)
                    .map(([s, count]) => {
                      const total = data.total_user_messages || 1;
                      const pct = Math.round((count / total) * 100);
                      return (
                        <div key={s}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                            <span style={{ fontSize: '12px', color: 'var(--text-secondary)',
                              textTransform: 'capitalize' }}>{s}</span>
                            <span style={{ fontSize: '12px', color: sentimentColor[s] || 'var(--text-muted)',
                              fontWeight: 600 }}>{pct}%</span>
                          </div>
                          <div style={styles.progressTrack}>
                            <div style={{
                              ...styles.progressBar,
                              width: `${pct}%`,
                              background: sentimentColor[s] || 'var(--accent-primary)',
                            }} />
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Emotion breakdown */}
            {data.emotion_breakdown && Object.keys(data.emotion_breakdown).length > 0 && (
              <div style={styles.card}>
                <p style={styles.cardLabel}>Emotions</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px' }}>
                  {Object.entries(data.emotion_breakdown)
                    .sort(([, a], [, b]) => b - a)
                    .map(([emotion, count]) => {
                      const meta = getEmotionMeta(emotion);
                      return (
                        <div key={emotion} style={{
                          display: 'flex', alignItems: 'center', gap: '5px',
                          padding: '4px 10px', borderRadius: '99px',
                          background: `${meta.color}12`,
                          border: `1px solid ${meta.color}25`,
                        }}>
                          <span style={{ fontSize: '13px' }}>{meta.emoji}</span>
                          <span style={{ fontSize: '11px', color: meta.color, fontWeight: 600 }}>
                            {emotion}
                          </span>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>×{count}</span>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Total */}
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '4px' }}>
              Based on {data.total_user_messages} message{data.total_user_messages !== 1 ? 's' : ''}
            </p>
          </>
        )}
      </div>
    </aside>
  );
}

const styles = {
  panel: {
    width: '240px', flexShrink: 0,
    background: 'var(--bg-card)',
    borderLeft: '1px solid var(--border)',
    display: 'flex', flexDirection: 'column',
    height: '100vh', overflow: 'hidden',
  },
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '18px 16px 14px',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  headerTitle: {
    fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)',
  },
  refreshBtn: {
    background: 'none', border: 'none', cursor: 'pointer',
    padding: '4px', borderRadius: 'var(--radius-sm)',
    display: 'flex',
  },
  body: {
    flex: 1, overflowY: 'auto', padding: '14px 12px',
    display: 'flex', flexDirection: 'column', gap: '10px',
  },
  empty: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    gap: '12px', padding: '32px 12px',
  },
  card: {
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)', padding: '14px',
  },
  cardLabel: {
    fontSize: '11px', fontWeight: 600,
    color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em',
  },
  statPill: {
    display: 'flex', alignItems: 'center', gap: '5px',
    padding: '6px 10px', borderRadius: 'var(--radius-md)',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    flex: 1, justifyContent: 'center',
  },
  progressTrack: {
    height: '4px', borderRadius: '99px',
    background: 'var(--bg-elevated)',
  },
  progressBar: {
    height: '100%', borderRadius: '99px',
    transition: 'width 500ms var(--ease)',
  },
};
