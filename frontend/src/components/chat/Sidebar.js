import React, { useState, useEffect, useCallback } from "react";
import {
  Plus,
  MessageSquare,
  LogOut,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { sessionsAPI, messagesAPI } from "../../services/api";
import { formatSessionDate } from "../../utils/helpers";
import { Button, Spinner } from "../ui";
import toast from "react-hot-toast";

/** Truncate a string to maxLen chars */
const truncate = (str, maxLen = 36) =>
  str && str.length > maxLen ? str.slice(0, maxLen).trimEnd() + "…" : str;

/** Derive a readable title from the first user message of a session */
const deriveTitle = (firstUserMessage) => {
  if (!firstUserMessage) return null;
  // Strip voice/transcription prefix noise
  const text = firstUserMessage.transcription || firstUserMessage.content || "";
  if (!text || text === "🎙 Processing voice…") return null;
  return truncate(text);
};

export default function Sidebar({
  activeSessionId,
  onSelectSession,
  onNewSession,
}) {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [titles, setTitles] = useState({}); // sessionId → title string
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const fetchSessions = useCallback(async () => {
    try {
      const res = await sessionsAPI.list();
      const list = res.data;
      setSessions(list);

      // Fetch first message of each session to derive titles (in parallel, limit 1)
      const titleEntries = await Promise.all(
        list.map(async (session) => {
          try {
            const msgRes = await messagesAPI.history(session.id, 2);
            const firstUser = msgRes.data.find((m) => m.role === "user");
            return [session.id, deriveTitle(firstUser)];
          } catch {
            return [session.id, null];
          }
        }),
      );
      setTitles(Object.fromEntries(titleEntries));
    } catch {
      toast.error("Could not load sessions");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleNew = async () => {
    setCreating(true);
    try {
      const res = await sessionsAPI.create();
      const newSession = res.data;
      setSessions((prev) => [newSession, ...prev]);
      setTitles((prev) => ({ ...prev, [newSession.id]: null }));
      onNewSession(newSession);
    } catch {
      toast.error("Could not create session");
    } finally {
      setCreating(false);
    }
  };

  /** Called by parent when a new message is sent so we can update the title live */
  const refreshTitle = useCallback(async (sessionId) => {
    try {
      const msgRes = await messagesAPI.history(sessionId, 2);
      const firstUser = msgRes.data.find((m) => m.role === "user");
      const title = deriveTitle(firstUser);
      if (title) setTitles((prev) => ({ ...prev, [sessionId]: title }));
    } catch {}
  }, []);

  // Expose refreshTitle via a ref trick — parent doesn't need it for now,
  // but we auto-refresh when activeSessionId changes and titles[id] is still null
  useEffect(() => {
    if (activeSessionId && !titles[activeSessionId]) {
      refreshTitle(activeSessionId);
    }
  }, [activeSessionId, titles, refreshTitle]);

  return (
    <aside style={styles.sidebar}>
      {/* Brand */}
      <div style={styles.brand}>
        <div style={styles.brandIcon}>
          <Sparkles size={18} color="#C4B5FD" />
        </div>
        <span style={styles.brandName}>Solace</span>
      </div>

      {/* New session */}
      <div style={{ padding: "0 12px 12px" }}>
        <Button
          variant="outline"
          size="md"
          loading={creating}
          onClick={handleNew}
          style={{
            width: "100%",
            justifyContent: "flex-start",
            gap: "8px",
            borderColor: "var(--border)",
            color: "var(--text-secondary)",
          }}
        >
          <Plus size={16} />
          New conversation
        </Button>
      </div>

      {/* Session list */}
      <div style={styles.sessionList}>
        <p style={styles.listLabel}>Conversations</p>

        {loading ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              padding: "32px 0",
            }}
          >
            <Spinner size={22} />
          </div>
        ) : sessions.length === 0 ? (
          <div style={styles.empty}>
            <MessageSquare size={28} color="var(--text-muted)" />
            <p
              style={{
                fontSize: "13px",
                color: "var(--text-muted)",
                textAlign: "center",
              }}
            >
              No conversations yet.
              <br />
              Start one above.
            </p>
          </div>
        ) : (
          sessions.map((session) => {
            const title = titles[session.id];
            const isActive = activeSessionId === session.id;
            return (
              <button
                key={session.id}
                onClick={() => onSelectSession(session)}
                style={{
                  ...styles.sessionItem,
                  ...(isActive ? styles.sessionItemActive : {}),
                }}
              >
                <div style={styles.sessionIcon}>
                  <MessageSquare
                    size={14}
                    color={isActive ? "#C4B5FD" : "var(--text-muted)"}
                  />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={styles.sessionTitle}>
                    {title || formatSessionDate(session.created_at)}
                  </p>
                  {title && (
                    <p style={styles.sessionSub}>
                      {formatSessionDate(session.created_at)}
                    </p>
                  )}
                </div>
                {isActive && (
                  <ChevronRight size={14} color="var(--accent-primary)" />
                )}
              </button>
            );
          })
        )}
      </div>

      {/* User footer */}
      <div style={styles.userFooter}>
        <div style={styles.avatar}>
          {(user?.email?.[0] || "U").toUpperCase()}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p
            style={{
              fontSize: "13px",
              fontWeight: 500,
              color: "var(--text-primary)",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {user?.email}
          </p>
        </div>
        <button onClick={logout} style={styles.logoutBtn} title="Sign out">
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: "260px",
    flexShrink: 0,
    background: "var(--bg-card)",
    borderRight: "1px solid var(--border)",
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    overflow: "hidden",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "20px 16px 16px",
    borderBottom: "1px solid var(--border)",
    marginBottom: "12px",
  },
  brandIcon: {
    width: "32px",
    height: "32px",
    background: "var(--accent-glow)",
    border: "1px solid var(--border-accent)",
    borderRadius: "var(--radius-md)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  brandName: {
    fontSize: "16px",
    fontWeight: 700,
    color: "var(--text-primary)",
    letterSpacing: "-0.4px",
  },
  sessionList: { flex: 1, overflowY: "auto", padding: "0 12px" },
  listLabel: {
    fontSize: "11px",
    fontWeight: 600,
    color: "var(--text-muted)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    padding: "0 4px",
    marginBottom: "6px",
  },
  sessionItem: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "9px 10px",
    borderRadius: "var(--radius-md)",
    background: "transparent",
    border: "1px solid transparent",
    cursor: "pointer",
    transition: "background 150ms",
    marginBottom: "2px",
  },
  sessionItemActive: {
    background: "var(--accent-glow)",
    border: "1px solid var(--border-accent)",
  },
  sessionIcon: {
    width: "28px",
    height: "28px",
    background: "var(--bg-elevated)",
    borderRadius: "var(--radius-sm)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  sessionTitle: {
    fontSize: "13px",
    fontWeight: 500,
    color: "var(--text-primary)",
    textAlign: "left",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  sessionSub: {
    fontSize: "11px",
    color: "var(--text-muted)",
    textAlign: "left",
  },
  empty: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "10px",
    padding: "32px 16px",
  },
  userFooter: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "14px 16px",
    borderTop: "1px solid var(--border)",
    background: "var(--bg-card)",
  },
  avatar: {
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    background: "var(--accent-glow)",
    border: "1px solid var(--border-accent)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "13px",
    fontWeight: 600,
    color: "var(--accent-primary)",
    flexShrink: 0,
  },
  logoutBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--text-muted)",
    padding: "6px",
    borderRadius: "var(--radius-sm)",
    display: "flex",
  },
};
