import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';
import { authAPI } from '../services/api';

const STATE = { loading: 'loading', success: 'success', expired: 'expired', error: 'error' };

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus]   = useState(STATE.loading);
  const [message, setMessage] = useState('');
  const [email, setEmail]     = useState('');
  const [resending, setResending] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus(STATE.error);
      setMessage('No verification token found in this link.');
      return;
    }

    api.get(`/auth/verify-email?token=${token}`)
      .then(res => {
        setStatus(STATE.success);
        setMessage(res.data?.message || 'Your email has been verified.');
      })
      .catch(err => {
        const detail = err.response?.data?.detail;
        if (detail === 'TOKEN_EXPIRED') {
          setStatus(STATE.expired);
          setMessage(
            'Your verification link has expired. Enter your email below to receive a new one.'
          );
        } else {
          setStatus(STATE.error);
          setMessage(detail || 'This link is invalid. Please register again.');
        }
      });
  }, [searchParams]);

  const handleResend = async () => {
    if (!email.trim()) {
      toast.error('Please enter your email address.');
      return;
    }
    setResending(true);
    try {
      await authAPI.resendVerification(email.trim());
      toast.success('Verification email sent! Check your inbox.');
      setMessage('New verification email sent. Please check your inbox.');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail === 'This email is already verified.') {
        toast.success('Your email is already verified. You can log in.');
      } else {
        toast.error(detail || 'Could not send email. Please try again.');
      }
    } finally {
      setResending(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.glow} />
      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoIcon}><Sparkles size={18} color="#C4B5FD" /></div>
          <span style={styles.logoText}>Solace</span>
        </div>

        {/* Icon */}
        <div style={styles.iconWrap}>
          {status === STATE.loading  && <Loader2 size={40} color="#C4B5FD" style={{ animation: 'spin 1s linear infinite' }} />}
          {status === STATE.success  && <CheckCircle size={40} color="#14B8A6" />}
          {status === STATE.expired  && <RefreshCw size={40} color="#FBBF24" />}
          {status === STATE.error    && <XCircle size={40} color="#FB7185" />}
        </div>

        <h1 style={styles.heading}>
          {status === STATE.loading && 'Verifying your email…'}
          {status === STATE.success && 'Email verified!'}
          {status === STATE.expired && 'Link expired'}
          {status === STATE.error   && 'Verification failed'}
        </h1>

        <p style={styles.sub}>{message}</p>

        {/* Success */}
        {status === STATE.success && (
          <Link to="/login" style={styles.btn}>Sign in to Solace</Link>
        )}

        {/* Expired — resend form */}
        {status === STATE.expired && (
          <div style={{ width: '100%' }}>
            <input
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={styles.input}
            />
            <button
              onClick={handleResend}
              disabled={resending}
              style={styles.btn}
            >
              {resending ? 'Sending…' : 'Resend verification email'}
            </button>
            <Link to="/login" style={styles.link}>Back to login</Link>
          </div>
        )}

        {/* Invalid */}
        {status === STATE.error && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%' }}>
            <Link to="/register" style={styles.btn}>Create a new account</Link>
            <Link to="/login" style={styles.link}>Back to login</Link>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '24px', background: 'var(--bg-base)', position: 'relative',
  },
  glow: {
    position: 'fixed', top: '-200px', left: '50%', transform: 'translateX(-50%)',
    width: '600px', height: '600px', borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(196,181,253,0.08) 0%, transparent 70%)',
    pointerEvents: 'none',
  },
  card: {
    width: '100%', maxWidth: '400px',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-xl)', padding: '40px',
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    gap: '0', position: 'relative', zIndex: 1,
  },
  logo: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px', alignSelf: 'flex-start' },
  logoIcon: {
    width: '32px', height: '32px', background: 'var(--accent-glow)',
    border: '1px solid var(--border-accent)', borderRadius: 'var(--radius-md)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  logoText: { fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.4px' },
  iconWrap: {
    width: '72px', height: '72px', borderRadius: '50%',
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px',
  },
  heading: {
    fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)',
    letterSpacing: '-0.4px', marginBottom: '10px', textAlign: 'center',
  },
  sub: {
    fontSize: '14px', color: 'var(--text-secondary)',
    textAlign: 'center', lineHeight: 1.7, marginBottom: '24px',
  },
  input: {
    width: '100%', height: '44px', padding: '0 14px',
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)', color: 'var(--text-primary)',
    fontSize: '14px', fontFamily: 'var(--font-ui)', outline: 'none',
    marginBottom: '12px',
  },
  btn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    width: '100%', height: '44px', borderRadius: 'var(--radius-xl)',
    background: 'var(--accent-primary)', color: '#0D1117',
    fontSize: '14px', fontWeight: 600, textDecoration: 'none',
    fontFamily: 'var(--font-ui)', border: 'none', cursor: 'pointer',
    marginBottom: '10px',
  },
  link: {
    display: 'block', textAlign: 'center', fontSize: '13px',
    color: 'var(--accent-primary)', textDecoration: 'none', marginTop: '8px',
  },
};