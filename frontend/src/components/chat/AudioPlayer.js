import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Play, Pause } from 'lucide-react';

/**
 * AudioPlayer
 * Props:
 *   base64audio : string  — base64-encoded audio from API
 *   mimeType    : string  — "audio/wav" or "audio/mpeg" (default: "audio/wav")
 *   autoPlay    : bool
 */
export default function AudioPlayer({ base64audio, mimeType = 'audio/wav', autoPlay = true }) {
  const audioRef              = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [error,   setError]   = useState(false);

  useEffect(() => {
    if (!base64audio) return;

    // Clean up any previous audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioRef.current = null;
    }

    setPlaying(false);
    setError(false);

    const audio = new Audio();
    // Use correct MIME type so browser knows how to decode
    audio.src = `data:${mimeType};base64,${base64audio}`;
    audioRef.current = audio;

    audio.onplay  = () => setPlaying(true);
    audio.onpause = () => setPlaying(false);
    audio.onended = () => setPlaying(false);
    audio.onerror = (e) => {
      console.error('AudioPlayer error:', e, audio.error);
      setError(true);
      setPlaying(false);
    };

    if (autoPlay) {
      // 400ms delay — gives browser time to finish rendering
      // and keeps within the user-gesture window from clicking Send
      const t = setTimeout(() => {
        audio.play().catch(err => {
          // NotAllowedError = browser blocked autoplay
          // User can still click the Play button
          console.warn('Autoplay blocked:', err.message);
        });
      }, 400);
      return () => {
        clearTimeout(t);
        audio.pause();
        audio.src = '';
      };
    }

    return () => {
      audio.pause();
      audio.src = '';
    };
  }, [base64audio, mimeType]);

  const toggle = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) { audio.pause(); }
    else         { audio.play().catch(() => {}); }
  }, [playing]);

  if (!base64audio || error) return null;

  return (
    <button
      onClick={toggle}
      aria-label={playing ? 'Pause' : 'Play voice response'}
      style={{
        display:      'inline-flex',
        alignItems:   'center',
        gap:          '6px',
        marginTop:    '10px',
        padding:      '5px 12px',
        borderRadius: '99px',
        border:       `1px solid ${playing ? 'rgba(196,181,253,0.4)' : 'var(--border)'}`,
        background:   playing ? 'rgba(196,181,253,0.1)' : 'var(--bg-elevated)',
        cursor:       'pointer',
        transition:   'all 150ms',
        userSelect:   'none',
      }}
    >
      {playing
        ? <Pause size={12} color="#C4B5FD" />
        : <Play  size={12} color="var(--text-secondary)" />
      }
      <span style={{
        fontSize:   '12px',
        fontWeight: 500,
        color:      playing ? '#C4B5FD' : 'var(--text-secondary)',
        fontFamily: 'var(--font-ui)',
      }}>
        {playing ? 'Playing…' : 'Play response'}
      </span>
      {playing && (
        <span style={{ display: 'flex', gap: '2px', alignItems: 'center' }}>
          {[1, 2, 3].map(i => (
            <span key={i} style={{
              display:         'block',
              width:           '2px',
              borderRadius:    '1px',
              background:      '#C4B5FD',
              height:          `${4 + i * 3}px`,
              animation:       `soundwave 0.7s ease-in-out ${i * 0.12}s infinite alternate`,
            }} />
          ))}
        </span>
      )}
    </button>
  );
}