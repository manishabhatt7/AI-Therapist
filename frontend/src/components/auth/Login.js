import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';
import { Button, Input } from '../ui';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Enter a valid email';
    if (!form.password) e.password = 'Password is required';
    return e;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/chat');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      {/* Ambient glow */}
      <div style={styles.glow} />

      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoIcon}><Sparkles size={20} color="#C4B5FD" /></div>
          <span style={styles.logoText}>Solace</span>
        </div>

        <h1 style={styles.heading}>Welcome back</h1>
        <p style={styles.sub}>A safe space, whenever you need it.</p>

        <form onSubmit={handleSubmit} style={styles.form} noValidate>
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            icon={Mail}
            value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            error={errors.email}
            autoComplete="email"
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            icon={Lock}
            value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            error={errors.password}
            autoComplete="current-password"
          />

          <Button type="submit" variant="primary" size="lg" loading={loading}
            style={{ width: '100%', marginTop: '8px' }}>
            Sign in
          </Button>
        </form>

        <p style={styles.footer}>
          New to Solace?{' '}
          <Link to="/register" style={styles.link}>Create an account</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '24px', position: 'relative', overflow: 'hidden',
    background: 'var(--bg-base)',
  },
  glow: {
    position: 'fixed', top: '-200px', left: '50%', transform: 'translateX(-50%)',
    width: '600px', height: '600px', borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(196,181,253,0.08) 0%, transparent 70%)',
    pointerEvents: 'none',
  },
  card: {
    width: '100%', maxWidth: '400px',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-xl)',
    padding: '40px',
    position: 'relative', zIndex: 1,
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px',
  },
  logoIcon: {
    width: '36px', height: '36px',
    background: 'var(--accent-glow)',
    border: '1px solid var(--border-accent)',
    borderRadius: 'var(--radius-md)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  logoText: {
    fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.5px',
  },
  heading: {
    fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)',
    letterSpacing: '-0.5px', marginBottom: '6px',
  },
  sub: {
    fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '28px',
  },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
  footer: { marginTop: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-secondary)' },
  link: { color: 'var(--accent-primary)', textDecoration: 'none', fontWeight: 500 },
};
