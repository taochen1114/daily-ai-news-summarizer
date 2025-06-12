import React from 'react';
import { FiPlay, FiPause, FiExternalLink } from 'react-icons/fi';

interface Article {
  id: string;
  title: string;
  url: string;
  source: string;
  summary: string;
  audio_file: string;
  published_date?: string;
  content_type: string;
}

interface ArticleCardProps {
  article: Article;
  isPlaying: boolean;
  onPlay: () => void;
}

const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  isPlaying,
  onPlay,
}) => {
  const sourceColor =
    article.content_type === 'academic'
      ? 'bg-blue-100 text-blue-800'
      : 'bg-green-100 text-green-800';

  return (
    <div className="overflow-hidden rounded-lg border border-gray-100 bg-white shadow-sm transition-shadow hover:shadow-md">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-2 flex items-center space-x-2">
              <span className={`rounded-full px-2 py-1 text-xs ${sourceColor}`}>
                {article.source}
              </span>

              {article.content_type === 'academic' && (
                <span className="rounded-full bg-purple-100 px-2 py-1 text-xs text-purple-800">
                  學術論文
                </span>
              )}

              {article.content_type === 'news' && (
                <span className="rounded-full bg-orange-100 px-2 py-1 text-xs text-orange-800">
                  新聞
                </span>
              )}
            </div>

            <h2 className="mb-2 text-xl font-semibold text-gray-800">
              {article.title}
            </h2>

            <p className="mb-4 text-sm text-gray-600">{article.summary}</p>

            <div className="flex items-center space-x-4">
              <button
                onClick={onPlay}
                className={`inline-flex items-center rounded-md px-4 py-2 text-sm font-medium ${
                  isPlaying
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-primary-500 text-white hover:bg-primary-600'
                }`}
              >
                {isPlaying ? (
                  <FiPause className="mr-2" />
                ) : (
                  <FiPlay className="mr-2" />
                )}
                {isPlaying ? '暫停播放' : '播放摘要'}
              </button>

              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
              >
                <FiExternalLink className="mr-2" />
                原文連結
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleCard;
