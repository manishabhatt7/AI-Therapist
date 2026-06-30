import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ChatPage from './pages/ChatPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import { Spinner } from './components/ui';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Spinner size={28} />
    </div>
  );
  return user ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? <Navigate to="/chat" replace /> : children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-center"
          toastOptions={{
            style: {
              background: '#1C2333', color: '#F8F7FF',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '12px', fontSize: '14px',
            },
            success: { iconTheme: { primary: '#14B8A6', secondary: '#0D1117' } },
            error:   { iconTheme: { primary: '#FB7185', secondary: '#0D1117' } },
          }}
        />

        <style>{`
          @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30%            { transform: translateY(-5px); opacity: 1; }
          }
          @keyframes soundwave {
            from { transform: scaleY(0.4); }
            to   { transform: scaleY(1.2); }
          }
          .animate-spin { animation: spin 1s linear infinite; }
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px rgba(196,181,253,0.08) !important;
          }
          textarea::placeholder { color: var(--text-muted); }
          button:active:not(:disabled) { transform: scale(0.97); }
        `}</style>

        <Routes>
          <Route path="/"             element={<Navigate to="/chat" replace />} />
          <Route path="/login"        element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register"     element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/chat"         element={<PrivateRoute><ChatPage /></PrivateRoute>} />
          <Route path="*"             element={<Navigate to="/chat" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}