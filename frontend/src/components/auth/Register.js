import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';
import { Button, Input } from '../ui';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.full_name.trim()) e.full_name = 'Name is required';
    if (!form.email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Enter a valid email';
    if (!form.password) e.password = 'Password is required';
    else if (form.password.length < 8) e.password = 'At least 8 characters';
    if (form.password !== form.confirm) e.confirm = 'Passwords do not match';
    return e;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setLoading(true);
    try {
      await register(form.email, form.password, form.full_name);
      toast.success('Account created! Check your email to verify.');
      navigate('/login');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const field = (key) => ({
    value: form[key],
    onChange: e => setForm(f => ({ ...f, [key]: e.target.value })),
    error: errors[key],
  });

  return (
    <div style={styles.page}>
      <div style={styles.glow} />
      <div style={styles.card}>
        <div style={styles.logo}>
          <div style={styles.logoIcon}><Sparkles size={20} color="#C4B5FD" /></div>
          <span style={styles.logoText}>Solace</span>
        </div>

        <h1 style={styles.heading}>Create your space</h1>
        <p style={styles.sub}>Confidential. Supportive. Always here.</p>

        <form onSubmit={handleSubmit} style={styles.form} noValidate>
          <Input label="Full name" placeholder="Alex Johnson" icon={User}
            autoComplete="name" {...field('full_name')} />
          <Input label="Email" type="email" placeholder="you@example.com" icon={Mail}
            autoComplete="email" {...field('email')} />
          <Input label="Password" type="password" placeholder="••••••••" icon={Lock}
            autoComplete="new-password" hint="At least 8 characters" {...field('password')} />
          <Input label="Confirm password" type="password" placeholder="••••••••" icon={Lock}
            autoComplete="new-password" {...field('confirm')} />

          <Button type="submit" variant="primary" size="lg" loading={loading}
            style={{ width: '100%', marginTop: '8px' }}>
            Create account
          </Button>
        </form>

        <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--accent-primary)', textDecoration: 'none', fontWeight: 500 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '24px', position: 'relative', background: 'var(--bg-base)',
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
    borderRadius: 'var(--radius-xl)', padding: '40px', position: 'relative', zIndex: 1,
  },
  logo: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' },
  logoIcon: {
    width: '36px', height: '36px', background: 'var(--accent-glow)',
    border: '1px solid var(--border-accent)', borderRadius: 'var(--radius-md)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  logoText: { fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.5px' },
  heading: { fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.5px', marginBottom: '6px' },
  sub: { fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '28px' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
};
