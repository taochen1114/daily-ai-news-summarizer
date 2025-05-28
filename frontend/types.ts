export interface Article {
  id: string;
  title: string;
  url: string;
  source: string;
  summary: string;
  audio_file: string;
  published_date?: string;
  content_type: string;
}

export interface ArticleListProps {
  articles: Article[];
  onPlay: (article: Article) => void;
  currentPlayingId: string | null;
}

export interface DateSelectorProps {
  dates: string[];
  selectedDate: string;
  onSelectDate: (date: string) => void;
}

export interface AudioPlayerProps {
  article: Article;
  onClose: () => void;
} 