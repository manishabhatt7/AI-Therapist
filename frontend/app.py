import os
import streamlit as st
from dotenv import load_dotenv

from api_client import APIClient
from utils import (
    get_emotion_meta,
    format_timestamp,
    format_session_date,
    decode_base64_audio,
    truncate,
    SENTIMENT_COLORS,
)
from styles import CUSTOM_CSS

load_dotenv()

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Solace | AI Therapist",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize API Client
api = APIClient()


# ── Session State Management ────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "session_titles" not in st.session_state:
    st.session_state.session_titles = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_enabled" not in st.session_state:
    st.session_state.audio_enabled = True
if "sentiment_data" not in st.session_state:
    st.session_state.sentiment_data = None
if "crisis_detected" not in st.session_state:
    st.session_state.crisis_detected = False


# ── Helper Functions ────────────────────────────────────────────────
def logout():
    if st.session_state.token:
        try:
            api.logout(st.session_state.token)
        except Exception:
            pass
    st.session_state.token = None
    st.session_state.user_email = None
    st.session_state.active_session_id = None
    st.session_state.sessions = []
    st.session_state.session_titles = {}
    st.session_state.messages = []
    st.session_state.sentiment_data = None
    st.session_state.crisis_detected = False
    st.rerun()


def fetch_sessions():
    if not st.session_state.token:
        return
    ok, res = api.list_sessions(st.session_state.token)
    if ok and isinstance(res, list):
        st.session_state.sessions = res
        # If no active session, select the most recent one or create new
        if not st.session_state.active_session_id and len(res) > 0:
            st.session_state.active_session_id = res[0]["id"]
            fetch_messages(res[0]["id"])
    else:
        st.session_state.sessions = []


def fetch_messages(session_id: str):
    if not st.session_state.token or not session_id:
        return
    ok, res = api.get_messages(st.session_state.token, session_id)
    if ok and isinstance(res, list):
        st.session_state.messages = res
        # Check crisis status in existing messages
        st.session_state.crisis_detected = any(
            m.get("crisis_flag") for m in res
        )
        # Derive title for sidebar if available
        first_user = next((m for m in res if m.get("role") == "user"), None)
        if first_user:
            text = (
                first_user.get("transcription")
                or first_user.get("content")
                or ""
            )
            st.session_state.session_titles[session_id] = truncate(text, 30)
    else:
        st.session_state.messages = []

    # Fetch sentiment summary
    fetch_sentiment_summary(session_id)


def fetch_sentiment_summary(session_id: str):
    if not st.session_state.token or not session_id:
        return
    ok, res = api.get_sentiment_summary(st.session_state.token, session_id)
    if ok and isinstance(res, dict) and "dominant_emotion_overall" in res:
        st.session_state.sentiment_data = res
        if res.get("crisis_flag_count", 0) > 0:
            st.session_state.crisis_detected = True
    else:
        st.session_state.sentiment_data = None


def create_new_session():
    if not st.session_state.token:
        return
    ok, res = api.create_session(st.session_state.token)
    if ok and isinstance(res, dict) and "id" in res:
        new_id = res["id"]
        st.session_state.active_session_id = new_id
        st.session_state.messages = []
        st.session_state.sentiment_data = None
        st.session_state.crisis_detected = False
        st.session_state.session_titles[new_id] = "New conversation"
        fetch_sessions()
        st.rerun()
    else:
        st.error(f"Failed to create new conversation: {res}")


# ── URL Query Parameters (Auto-Verification) ────────────────────────
token_param = st.query_params.get("token")
if token_param and not st.session_state.token:
    with st.container():
        st.info("🔄 Verifying your email...")
        ok, res = api.verify_email(token_param)
        if ok:
            st.success("✅ " + (res.get("message") if isinstance(res, dict) else "Email verified successfully! You can now log in."))
            st.query_params.clear()
        else:
            if "TOKEN_EXPIRED" in str(res):
                st.warning("⚠️ Your verification link has expired. Please request a new verification email below.")
            else:
                st.error(f"❌ Verification error: {res}")


# ── View 1: Authentication View ─────────────────────────────────────
if not st.session_state.token:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 30px; margin-bottom: 25px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: rgba(167, 139, 250, 0.15); border: 1px solid rgba(167, 139, 250, 0.35); border-radius: 18px; font-size: 32px; margin-bottom: 12px;">
                    ✨
                </div>
                <h1 style="font-size: 2rem; font-weight: 700; margin: 0; color: #F8FAFC; letter-spacing: -0.5px;">Solace</h1>
                <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 6px;">A compassionate, confidential space for your thoughts & feelings.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔐 Sign In", "📝 Create Account", "✉️ Email Verification"])

        # ── Sign In Tab ──
        with auth_tab1:
            with st.form("login_form"):
                st.markdown("##### Welcome Back")
                email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
                submitted = st.form_submit_button("Sign In", width="stretch", type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        with st.spinner("Signing in..."):
                            ok, res = api.login(email.strip(), password)
                            if ok and isinstance(res, dict) and "access_token" in res:
                                st.session_state.token = res["access_token"]
                                st.session_state.user_email = email.strip()
                                st.toast("Welcome back!", icon="💜")
                                fetch_sessions()
                                st.rerun()
                            else:
                                if "EMAIL_NOT_VERIFIED" in str(res):
                                    st.warning("⚠️ Your email has not been verified yet. Please check your inbox or use the 'Email Verification' tab to resend a link.")
                                else:
                                    st.error(f"Login failed: {res}")

        # ── Register Tab ──
        with auth_tab2:
            with st.form("register_form"):
                st.markdown("##### Create your confidential space")
                full_name = st.text_input("Full Name", placeholder="Alex Johnson", key="reg_name")
                reg_email = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
                reg_password = st.text_input("Password", type="password", placeholder="At least 8 characters", key="reg_pass")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_confirm")
                reg_submitted = st.form_submit_button("Create Account", width="stretch", type="primary")

                if reg_submitted:
                    if not full_name or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Creating account..."):
                            ok, res = api.register(reg_email.strip(), reg_password, full_name.strip())
                            if ok:
                                st.success("🎉 Account created! Please check your email inbox to verify your account before logging in.")
                            else:
                                st.error(f"Registration failed: {res}")

        # ── Verify & Resend Tab ──
        with auth_tab3:
            st.markdown("##### Verify Email or Resend Link")
            verify_token = st.text_input("Verification Token", placeholder="Paste token from email link", key="manual_token")
            if st.button("Verify Token", width="stretch"):
                if verify_token:
                    with st.spinner("Verifying token..."):
                        ok, res = api.verify_email(verify_token.strip())
                        if ok:
                            st.success("✅ Email verified successfully! You can now sign in.")
                        else:
                            st.error(f"Verification failed: {res}")
                else:
                    st.error("Please enter a token.")

            st.divider()
            st.markdown("##### Resend Verification Email")
            resend_email = st.text_input("Registered Email", placeholder="you@example.com", key="resend_email")
            if st.button("Resend Verification Email", width="stretch"):
                if resend_email:
                    with st.spinner("Sending email..."):
                        ok, res = api.resend_verification(resend_email.strip())
                        if ok:
                            st.success("✉️ Verification email sent! Please check your inbox.")
                        else:
                            st.error(f"Could not resend email: {res}")
                else:
                    st.error("Please enter your email.")


# ── View 2: Main AI Therapist Chat Application ──────────────────────
else:
    # ── Sidebar ──
    with st.sidebar:
        # Solace Brand Header
        st.markdown(
            """
            <div class="solace-brand-header">
                <div class="solace-brand-icon">💜</div>
                <div>
                    <h3 class="solace-brand-title">Solace</h3>
                    <p class="solace-brand-sub">AI Therapist · always here</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Logged-in User Profile
        user_initial = (st.session_state.user_email[0].upper() if st.session_state.user_email else "U")
        st.markdown(
            f"""
            <div class="user-profile-badge">
                <div class="user-avatar">{user_initial}</div>
                <div class="user-email-text" title="{st.session_state.user_email}">{st.session_state.user_email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # New Session Button
        if st.button("➕ New Conversation", width="stretch", type="primary"):
            create_new_session()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.markdown("###### Conversations")

        # Load session list if empty
        if not st.session_state.sessions:
            fetch_sessions()

        if not st.session_state.sessions:
            st.caption("No conversations yet. Start one above!")
        else:
            for s in st.session_state.sessions:
                s_id = s["id"]
                is_active = (s_id == st.session_state.active_session_id)
                title = st.session_state.session_titles.get(s_id) or format_session_date(s.get("created_at"))
                icon = "💬" if not is_active else "💜"
                btn_type = "secondary"

                if st.button(
                    f"{icon} {title}",
                    key=f"session_btn_{s_id}",
                    width="stretch",
                    disabled=is_active,
                ):
                    st.session_state.active_session_id = s_id
                    fetch_messages(s_id)
                    st.rerun()

        st.divider()

        # Settings & Controls
        st.session_state.audio_enabled = st.toggle(
            "🔊 Voice Audio Responses",
            value=st.session_state.audio_enabled,
            help="When enabled, Solace synthesizes warm spoken audio for responses."
        )

        if st.button("🚪 Sign Out", width="stretch"):
            logout()

    # ── Main Content Area ──
    # Ensure active session exists
    if not st.session_state.active_session_id:
        if st.session_state.sessions:
            st.session_state.active_session_id = st.session_state.sessions[0]["id"]
            fetch_messages(st.session_state.active_session_id)
        else:
            create_new_session()

    # Header Bar
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem; font-weight: 700; color: #F8FAFC;">Solace Session</span>
                <span class="online-badge"><span class="online-dot"></span> Online & Listening</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_col2:
        show_insights = st.toggle("📊 Insights Panel", value=False)

    # ── Crisis Support Banner (if detected) ──
    if st.session_state.crisis_detected:
        st.markdown(
            """
            <div class="crisis-alert-box">
                <h4>🆘 We are here with you & support is available</h4>
                <p>If you or someone you know is going through a crisis or having thoughts of self-harm, please reach out to trusted support immediately. You don't have to carry this alone.</p>
                <div style="margin-top: 8px; font-weight: 600; font-size: 0.88rem;">
                    📞 Call or Text <strong>988</strong> (Suicide & Crisis Lifeline - Free, 24/7, Confidential)<br/>
                    💬 Text <strong>HOME</strong> to <strong>741741</strong> (Crisis Text Line)<br/>
                    🌍 International Resources: <a href="https://findahelpline.com" target="_blank" style="color: #FFE4E6; text-decoration: underline;">findahelpline.com</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Session Insights Panel ──
    if show_insights:
        data = st.session_state.sentiment_data
        with st.expander("📊 Session Emotional Insights & Sentiment Breakdown", expanded=True):
            if not data or not data.get("dominant_emotion_overall"):
                st.info("Insights and emotional tracking will appear as you chat with Solace.")
            else:
                dom_meta = get_emotion_meta(data.get("dominant_emotion_overall"))
                icols = st.columns([1, 1, 1, 1])
                with icols[0]:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Primary Emotion</div>
                            <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                                <span style="font-size: 1.5rem;">{dom_meta['emoji']}</span>
                                <span style="font-size: 1.1rem; font-weight: 700; color: {dom_meta['color']};">{dom_meta['label']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with icols[1]:
                    conf = int(data.get("average_confidence", 0) * 100) if data.get("average_confidence") else "—"
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Avg Confidence</div>
                            <div class="metric-value">{conf}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with icols[2]:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Messages</div>
                            <div class="metric-value">{data.get('total_user_messages', 0)} <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 400;">({data.get('text_message_count', 0)} text / {data.get('voice_message_count', 0)} voice)</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with icols[3]:
                    crisis_c = data.get("crisis_flag_count", 0)
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Crisis Flags</div>
                            <div class="metric-value" style="color: {'#FB7185' if crisis_c > 0 else '#34D399'};">{crisis_c}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Sentiment & Emotion distribution
                col_s, col_e = st.columns(2)
                with col_s:
                    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #94A3B8; margin-bottom: 4px;'>SENTIMENT BREAKDOWN</p>", unsafe_allow_html=True)
                    sb = data.get("sentiment_breakdown", {})
                    total = data.get("total_user_messages", 1) or 1
                    for sent, count in sb.items():
                        pct = int((count / total) * 100)
                        scolor = SENTIMENT_COLORS.get(sent.lower(), "#A78BFA")
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 2px;">
                                <span style="text-transform: capitalize; color: #E2E8F0;">{sent}</span>
                                <span style="font-weight: 600; color: {scolor};">{pct}% ({count})</span>
                            </div>
                            <div style="width: 100%; height: 5px; background: rgba(255,255,255,0.08); border-radius: 4px; margin-bottom: 8px;">
                                <div style="width: {pct}%; height: 100%; background: {scolor}; border-radius: 4px;"></div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                with col_e:
                    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #94A3B8; margin-bottom: 4px;'>DETECTED EMOTIONS</p>", unsafe_allow_html=True)
                    eb = data.get("emotion_breakdown", {})
                    badges_html = "<div style='display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;'>"
                    for emo, count in eb.items():
                        meta = get_emotion_meta(emo)
                        badges_html += f"""
                        <span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 99px; background: {meta['color']}18; border: 1px solid {meta['color']}40; color: {meta['color']}; font-size: 0.75rem; font-weight: 600;">
                            {meta['emoji']} {emo} ×{count}
                        </span>
                        """
                    badges_html += "</div>"
                    st.markdown(badges_html, unsafe_allow_html=True)

    # ── Chat Messages Display ──
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                """
                <div style="text-align: center; padding: 40px 20px; color: #94A3B8;">
                    <div style="font-size: 2.2rem; margin-bottom: 12px;">💜</div>
                    <h3 style="color: #F8FAFC; margin-bottom: 8px;">Your space to talk</h3>
                    <p style="font-size: 0.9rem; max-width: 480px; margin: 0 auto; line-height: 1.6;">
                        Share whatever is weighing on you today. You can write a message or record your voice below. Solace is here to listen without judgment.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.messages:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                is_voice = (msg.get("input_type") == "voice")
                transcription = msg.get("transcription")
                dominant_emotion = msg.get("dominant_emotion")
                audio_base64 = msg.get("audio_base64")
                audio_mime = msg.get("audio_mime") or "audio/wav"
                created_at = msg.get("created_at")

                if role == "user":
                    with st.chat_message("user"):
                        if is_voice:
                            st.markdown('<div class="voice-badge">🎙️ Voice Message</div>', unsafe_allow_html=True)
                            if transcription and transcription != content:
                                st.caption(f'"{transcription}"')
                        st.markdown(content)

                        # Emotion Badge and Timestamp
                        if dominant_emotion:
                            meta = get_emotion_meta(dominant_emotion)
                            st.markdown(
                                f"""
                                <span class="emotion-badge" style="background: {meta['color']}15; border: 1px solid {meta['color']}35; color: {meta['color']};">
                                    {meta['emoji']} {meta['label']}
                                </span>
                                """,
                                unsafe_allow_html=True,
                            )
                        if created_at:
                            st.caption(format_timestamp(created_at))

                else:
                    with st.chat_message("assistant", avatar="💜"):
                        st.markdown(content)
                        if audio_base64:
                            audio_bytes = decode_base64_audio(audio_base64)
                            if audio_bytes:
                                st.audio(audio_bytes, format=audio_mime)
                        if created_at:
                            st.caption(format_timestamp(created_at))

    # ── Voice Recording & Audio File Upload Expander ──
    with st.expander("🎙️ Voice Message (Record or Upload Audio)", expanded=False):
        v_col1, v_col2 = st.columns(2)
        recorded_audio = None
        uploaded_audio = None

        with v_col1:
            st.markdown("###### 🎤 Record Voice")
            try:
                # Modern Streamlit audio input widget
                recorded_audio = st.audio_input("Record your thoughts")
            except Exception:
                st.caption("Microphone recording is ready via file uploader.")

        with v_col2:
            st.markdown("###### 📁 Or Upload Audio File")
            uploaded_audio = st.file_uploader(
                "Upload voice recording",
                type=["wav", "mp3", "m4a", "ogg", "webm"],
                key="voice_file_uploader",
                help="Supports WAV, MP3, M4A, OGG, and WebM audio formats."
            )

        voice_to_send = recorded_audio or uploaded_audio
        if voice_to_send:
            fname = getattr(voice_to_send, "name", "recording.wav") or "recording.wav"
            if st.button("🚀 Send Voice Message", key="btn_send_voice", type="primary"):
                with st.spinner("Processing voice & transcribing..."):
                    audio_data = voice_to_send.getvalue()
                    ok, res = api.send_voice_message(
                        token=st.session_state.token,
                        session_id=st.session_state.active_session_id,
                        audio_bytes=audio_data,
                        filename=fname,
                        tts=st.session_state.audio_enabled,
                    )
                    if ok and isinstance(res, dict):
                        # Reload messages
                        fetch_messages(st.session_state.active_session_id)
                        st.rerun()
                    else:
                        st.error(f"Failed to process voice message: {res}")

    # ── Text Chat Input ──
    user_input = st.chat_input("Share what's on your mind...")
    if user_input:
        user_text = user_input.strip()
        if user_text and st.session_state.active_session_id:
            # Add optimistic message to UI
            st.session_state.messages.append({
                "role": "user",
                "content": user_text,
                "input_type": "text",
            })

            with st.spinner("Solace is thinking..."):
                ok, res = api.send_message(
                    token=st.session_state.token,
                    session_id=st.session_state.active_session_id,
                    message=user_text,
                    tts=st.session_state.audio_enabled,
                )
                if ok and isinstance(res, dict):
                    # Refresh messages and insights
                    fetch_messages(st.session_state.active_session_id)
                    st.rerun()
                else:
                    st.error(f"Error sending message: {res}")
