import { formatDistanceToNow, format } from 'date-fns';

export const formatTime = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return format(d, 'h:mm a');
};

export const formatRelative = (dateStr) => {
  if (!dateStr) return '';
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
};

export const formatSessionDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now - d) / 86400000);
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  return format(d, 'MMM d');
};

export const formatDuration = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

/** Map emotion string → emoji + colour */
export const emotionMeta = {
  anxious:    { emoji: '😰', color: '#FBBF24', label: 'Anxious' },
  sad:        { emoji: '😢', color: '#60A5FA', label: 'Sad' },
  hopeful:    { emoji: '🌱', color: '#34D399', label: 'Hopeful' },
  frustrated: { emoji: '😤', color: '#FB7185', label: 'Frustrated' },
  calm:       { emoji: '😌', color: '#14B8A6', label: 'Calm' },
  angry:      { emoji: '😠', color: '#F87171', label: 'Angry' },
  confused:   { emoji: '😕', color: '#A78BFA', label: 'Confused' },
  grateful:   { emoji: '🙏', color: '#34D399', label: 'Grateful' },
  lonely:     { emoji: '🌧️', color: '#818CF8', label: 'Lonely' },
  relieved:   { emoji: '😮‍💨', color: '#6EE7B7', label: 'Relieved' },
  neutral:    { emoji: '😐', color: '#94A3B8', label: 'Neutral' },
};

export const getEmotionMeta = (emotion) =>
  emotionMeta[emotion?.toLowerCase()] || emotionMeta.neutral;

export const sentimentColor = {
  positive: '#34D399',
  negative: '#FB7185',
  neutral:  '#94A3B8',
  mixed:    '#FBBF24',
};
