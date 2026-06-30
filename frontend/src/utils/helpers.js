import { formatDistanceToNow, format } from 'date-fns';

export const formatTime = (dateStr) => {
  if (!dateStr) return '';
  return format(new Date(dateStr), 'h:mm a');
};

export const formatRelative = (dateStr) => {
  if (!dateStr) return '';
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
};

export const formatSessionDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const diffDays = Math.floor((new Date() - d) / 86400000);
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  return format(d, 'MMM d');
};

export const formatDuration = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

// ── Emotion metadata ──────────────────────────────────────────────
// Every value returned by sentiment_service must have an entry here.
// If a new emotion is added to the backend, add it here too.
export const emotionMeta = {
  // Crisis emotions
  desperate:   { emoji: '🆘', color: '#FB7185', label: 'Desperate' },
  numb:        { emoji: '😶', color: '#818CF8', label: 'Numb' },
  overwhelmed: { emoji: '😵', color: '#F87171', label: 'Overwhelmed' },
  fearful:     { emoji: '😨', color: '#FBBF24', label: 'Fearful' },
  ashamed:     { emoji: '😞', color: '#A78BFA', label: 'Ashamed' },

  // Negative emotions
  anxious:     { emoji: '😰', color: '#FBBF24', label: 'Anxious' },
  sad:         { emoji: '😢', color: '#60A5FA', label: 'Sad' },
  frustrated:  { emoji: '😤', color: '#FB923C', label: 'Frustrated' },
  angry:       { emoji: '😠', color: '#F87171', label: 'Angry' },
  lonely:      { emoji: '🌧️', color: '#818CF8', label: 'Lonely' },
  confused:    { emoji: '😕', color: '#A78BFA', label: 'Confused' },

  // Positive / neutral emotions
  hopeful:     { emoji: '🌱', color: '#34D399', label: 'Hopeful' },
  calm:        { emoji: '😌', color: '#14B8A6', label: 'Calm' },
  grateful:    { emoji: '🙏', color: '#34D399', label: 'Grateful' },
  relieved:    { emoji: '😮‍💨', color: '#6EE7B7', label: 'Relieved' },
  neutral:     { emoji: '😐', color: '#94A3B8', label: 'Neutral' },
};

export const getEmotionMeta = (emotion) => {
  if (!emotion) return emotionMeta.neutral;
  const key = emotion.toLowerCase().trim();
  return emotionMeta[key] || emotionMeta.neutral;
};

export const sentimentColor = {
  positive: '#34D399',
  negative: '#FB7185',
  neutral:  '#94A3B8',
  mixed:    '#FBBF24',
};