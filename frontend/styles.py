"""Custom CSS styles for Solace AI Therapist Streamlit UI."""

CUSTOM_CSS = """
<style>
/* Main App Styling */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Background gradient highlights */
.stApp {
    background: radial-gradient(circle at 50% -20%, rgba(167, 139, 250, 0.07), transparent 60%), #0D1117;
}

/* Header & Brand */
.solace-brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0 18px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 16px;
}

.solace-brand-icon {
    width: 38px;
    height: 38px;
    background: rgba(167, 139, 250, 0.15);
    border: 1px solid rgba(167, 139, 250, 0.35);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.solace-brand-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.5px;
    margin: 0;
}

.solace-brand-sub {
    font-size: 0.78rem;
    color: #94A3B8;
    margin: 0;
}

/* Chat Header */
.chat-header-bar {
    background: #161B22;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8rem;
    color: #34D399;
    background: rgba(52, 211, 153, 0.1);
    padding: 3px 8px;
    border-radius: 99px;
    border: 1px solid rgba(52, 211, 153, 0.2);
}

.online-dot {
    width: 7px;
    height: 7px;
    background: #34D399;
    border-radius: 50%;
    box-shadow: 0 0 6px #34D399;
}

/* Crisis Warning Alert */
.crisis-alert-box {
    background: linear-gradient(135deg, rgba(244, 63, 94, 0.15), rgba(244, 63, 94, 0.05));
    border: 1px solid rgba(244, 63, 94, 0.4);
    border-left: 4px solid #FB7185;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 14px 0 20px 0;
    color: #FECDD3;
}

.crisis-alert-box h4 {
    margin: 0 0 6px 0;
    font-size: 0.95rem;
    color: #FFE4E6;
    display: flex;
    align-items: center;
    gap: 8px;
}

.crisis-alert-box p {
    margin: 0;
    font-size: 0.84rem;
    line-height: 1.5;
    color: #FBCFE8;
}

/* Emotion Pill Badges */
.emotion-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 4px;
}

.voice-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    border-radius: 99px;
    font-size: 0.72rem;
    background: rgba(167, 139, 250, 0.12);
    color: #C4B5FD;
    border: 1px solid rgba(167, 139, 250, 0.25);
    margin-bottom: 4px;
}

/* Cards & Stats */
.metric-card {
    background: #161B22;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
}

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.15rem;
    font-weight: 700;
    color: #F8FAFC;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0D1117;
}
::-webkit-scrollbar-thumb {
    background: #30363D;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #8B5CF6;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #161B22;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Expander Styling */
.streamlit-expanderHeader {
    background-color: #161B22 !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* User Profile Badge in Sidebar */
.user-profile-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    margin-bottom: 12px;
}

.user-avatar {
    width: 28px;
    height: 28px;
    background: rgba(167, 139, 250, 0.2);
    border: 1px solid rgba(167, 139, 250, 0.4);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #C4B5FD;
    font-size: 0.8rem;
}

.user-email-text {
    font-size: 0.82rem;
    color: #E2E8F0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 170px;
}
</style>
"""

