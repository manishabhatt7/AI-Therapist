import React, { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { CheckCircle, XCircle, Loader2, Sparkles } from "lucide-react";
import api from "../services/api";

const STATE = { loading: "loading", success: "success", error: "error" };

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState(STATE.loading);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setStatus(STATE.error);
      setMessage(
        "No verification token found in the link. Please check your email and try again.",
      );
      return;
    }

    api
      .get(`/auth/verify-email?token=${token}`)
      .then((res) => {
        setStatus(STATE.success);
        setMessage(res.data?.message || "Your email has been verified.");
      })
      .catch((err) => {
        setStatus(STATE.error);
        setMessage(
          err.response?.data?.detail ||
            "This link is invalid or has expired. Please register again or contact support.",
        );
      });
  }, [searchParams]);

  return (
    <div style={styles.page}>
      <div style={styles.glow} />

      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoIcon}>
            <Sparkles size={18} color="#C4B5FD" />
          </div>
          <span style={styles.logoText}>Solace</span>
        </div>

        {/* Status icon */}
        <div style={styles.iconWrap}>
          {status === STATE.loading && (
            <Loader2
              size={40}
              color="#C4B5FD"
              style={{ animation: "spin 1s linear infinite" }}
            />
          )}
          {status === STATE.success && (
            <CheckCircle size={40} color="#14B8A6" />
          )}
          {status === STATE.error && <XCircle size={40} color="#FB7185" />}
        </div>

        {/* Heading */}
        <h1 style={styles.heading}>
          {status === STATE.loading && "Verifying your email…"}
          {status === STATE.success && "Email verified!"}
          {status === STATE.error && "Verification failed"}
        </h1>

        {/* Message */}
        <p style={styles.sub}>{message}</p>

        {/* CTA */}
        {status === STATE.success && (
          <Link to="/login" style={styles.btn}>
            Sign in to your account
          </Link>
        )}

        {status === STATE.error && (
          <Link to="/register" style={{ ...styles.btn, ...styles.btnOutline }}>
            Back to register
          </Link>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    background: "var(--bg-base)",
    position: "relative",
    overflow: "hidden",
  },
  glow: {
    position: "fixed",
    top: "-200px",
    left: "50%",
    transform: "translateX(-50%)",
    width: "600px",
    height: "600px",
    borderRadius: "50%",
    background:
      "radial-gradient(circle, rgba(196,181,253,0.08) 0%, transparent 70%)",
    pointerEvents: "none",
  },
  card: {
    width: "100%",
    maxWidth: "400px",
    background: "var(--bg-card)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-xl)",
    padding: "40px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0",
    position: "relative",
    zIndex: 1,
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "32px",
    alignSelf: "flex-start",
  },
  logoIcon: {
    width: "32px",
    height: "32px",
    background: "var(--accent-glow)",
    border: "1px solid var(--border-accent)",
    borderRadius: "var(--radius-md)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  logoText: {
    fontSize: "16px",
    fontWeight: 700,
    color: "var(--text-primary)",
    letterSpacing: "-0.4px",
  },
  iconWrap: {
    width: "72px",
    height: "72px",
    borderRadius: "50%",
    background: "var(--bg-elevated)",
    border: "1px solid var(--border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "20px",
  },
  heading: {
    fontSize: "20px",
    fontWeight: 700,
    color: "var(--text-primary)",
    letterSpacing: "-0.4px",
    marginBottom: "10px",
    textAlign: "center",
  },
  sub: {
    fontSize: "14px",
    color: "var(--text-secondary)",
    textAlign: "center",
    lineHeight: 1.7,
    marginBottom: "28px",
  },
  btn: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    height: "44px",
    padding: "0 24px",
    borderRadius: "var(--radius-xl)",
    background: "var(--accent-primary)",
    color: "#0D1117",
    fontSize: "14px",
    fontWeight: 600,
    textDecoration: "none",
    fontFamily: "var(--font-ui)",
    transition: "opacity 150ms",
  },
  btnOutline: {
    background: "transparent",
    border: "1px solid var(--border)",
    color: "var(--text-primary)",
  },
};
