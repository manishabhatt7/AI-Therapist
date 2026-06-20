# Solace – AI Therapist Frontend

React frontend for the Solace AI Therapist. Connects to the FastAPI backend.

## Stack

- **React 18** – UI framework
- **React Router v6** – client-side routing
- **Axios** – API calls with JWT interceptors
- **Framer Motion** – animations
- **React Hot Toast** – notifications
- **React Markdown** – render therapist responses with markdown
- **Lucide React** – icons
- **date-fns** – date formatting

## Setup

```bash
npm install
cp .env.example .env
npm start
```

Runs on http://localhost:3000. Proxies `/auth` and `/chat` to `http://localhost:8000`.

## Build for production

```bash
npm run build
```

## Structure

```
src/
├── components/
│   ├── auth/
│   │   ├── Login.js          # Login form
│   │   └── Register.js       # Registration form
│   ├── chat/
│   │   ├── Sidebar.js        # Session list + new session
│   │   ├── MessageBubble.js  # Chat bubble (text + voice)
│   │   ├── VoiceRecorder.js  # Record/preview/send audio
│   │   └── SentimentPanel.js # Emotion analytics panel
│   └── ui/
│       └── index.js          # Button, Input, Card, Badge, Spinner, Tooltip
├── context/
│   └── AuthContext.js        # Auth state + login/logout
├── hooks/
│   └── useVoiceRecorder.js   # MediaRecorder wrapper
├── pages/
│   └── ChatPage.js           # Main chat layout
├── services/
│   └── api.js                # Axios instance + all API calls
├── utils/
│   └── helpers.js            # Date formatting, emotion metadata
├── App.js                    # Router + providers
└── index.css                 # Design tokens + reset
```

## Design

- Dark navy base (`#0D1117`) with lavender accent (`#C4B5FD`)
- **Signature element:** Therapist reply bubbles use Lora serif font + lavender left-border glow — intentionally warm, not chatbot-like
- Inter for all UI chrome, Lora for all therapist content
- Teal (`#14B8A6`) = positive / online states
- Rose (`#FB7185`) = alerts / crisis flag

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend base URL | `""` (uses proxy) |
