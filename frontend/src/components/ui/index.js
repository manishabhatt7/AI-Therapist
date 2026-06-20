import React from 'react';
import { Loader2 } from 'lucide-react';

/* ── Button ─────────────────────────────────────────────────────── */
export function Button({
  children, variant = 'primary', size = 'md',
  loading = false, disabled = false,
  className = '', onClick, type = 'button', ...props
}) {
  const base = `
    inline-flex items-center justify-center gap-2 font-medium
    transition-all duration-200 focus-visible:outline
    disabled:opacity-50 disabled:cursor-not-allowed
    select-none cursor-pointer border-0
  `;

  const variants = {
    primary:  'bg-[#C4B5FD] text-[#0D1117] hover:bg-[#A78BFA] active:scale-[0.98]',
    ghost:    'bg-transparent text-[#94A3B8] hover:bg-[#1C2333] hover:text-[#F8F7FF]',
    danger:   'bg-[#FB7185]/10 text-[#FB7185] hover:bg-[#FB7185]/20',
    outline:  'bg-transparent border border-[rgba(255,255,255,0.1)] text-[#F8F7FF] hover:bg-[#1C2333]',
  };

  const sizes = {
    sm: 'h-8 px-3 text-sm rounded-md',
    md: 'h-10 px-4 text-sm rounded-xl',
    lg: 'h-12 px-6 text-base rounded-xl',
    icon: 'h-9 w-9 rounded-xl',
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      style={{ fontFamily: 'var(--font-ui)' }}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
}

/* ── Input ──────────────────────────────────────────────────────── */
export function Input({
  label, error, hint, icon: Icon,
  className = '', wrapperClass = '', ...props
}) {
  return (
    <div className={`flex flex-col gap-1.5 ${wrapperClass}`}>
      {label && (
        <label style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {label}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        {Icon && (
          <span style={{
            position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)',
            color: 'var(--text-muted)', pointerEvents: 'none'
          }}>
            <Icon size={16} />
          </span>
        )}
        <input
          style={{
            width: '100%',
            height: '44px',
            padding: Icon ? '0 14px 0 38px' : '0 14px',
            background: 'var(--bg-elevated)',
            border: error ? '1px solid var(--accent-rose)' : '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            fontFamily: 'var(--font-ui)',
            transition: 'border-color 200ms, box-shadow 200ms',
            outline: 'none',
          }}
          onFocus={e => e.target.style.borderColor = 'var(--accent-primary)'}
          onBlur={e => e.target.style.borderColor = error ? 'var(--accent-rose)' : 'var(--border)'}
          className={className}
          {...props}
        />
      </div>
      {error && <p style={{ fontSize: '12px', color: 'var(--accent-rose)' }}>{error}</p>}
      {hint && !error && <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{hint}</p>}
    </div>
  );
}

/* ── Card ───────────────────────────────────────────────────────── */
export function Card({ children, className = '', style = {}, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        ...style,
      }}
      className={className}
    >
      {children}
    </div>
  );
}

/* ── Spinner ────────────────────────────────────────────────────── */
export function Spinner({ size = 20 }) {
  return (
    <Loader2
      size={size}
      style={{ color: 'var(--accent-primary)', animation: 'spin 1s linear infinite' }}
    />
  );
}

/* ── Badge ──────────────────────────────────────────────────────── */
export function Badge({ children, color = '#C4B5FD', className = '' }) {
  return (
    <span
      style={{
        display: 'inline-flex', alignItems: 'center', gap: '4px',
        padding: '2px 8px', borderRadius: '99px',
        fontSize: '11px', fontWeight: 600,
        background: `${color}18`,
        color: color,
        border: `1px solid ${color}30`,
      }}
      className={className}
    >
      {children}
    </span>
  );
}

/* ── Tooltip ────────────────────────────────────────────────────── */
export function Tooltip({ children, text }) {
  return (
    <span style={{ position: 'relative', display: 'inline-flex' }}
      onMouseEnter={e => {
        const tip = e.currentTarget.querySelector('.tip');
        if (tip) tip.style.opacity = '1';
      }}
      onMouseLeave={e => {
        const tip = e.currentTarget.querySelector('.tip');
        if (tip) tip.style.opacity = '0';
      }}
    >
      {children}
      <span className="tip" style={{
        position: 'absolute', bottom: 'calc(100% + 6px)', left: '50%',
        transform: 'translateX(-50%)',
        background: '#1C2333', color: 'var(--text-primary)',
        fontSize: '11px', fontWeight: 500,
        padding: '4px 8px', borderRadius: '6px',
        whiteSpace: 'nowrap', pointerEvents: 'none',
        opacity: 0, transition: 'opacity 150ms',
        border: '1px solid var(--border)',
        zIndex: 50,
      }}>
        {text}
      </span>
    </span>
  );
}
