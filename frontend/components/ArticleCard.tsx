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

const ArticleCard: React.FC<ArticleCardProps> = ({ article, isPlaying, onPlay }) => {
  const sourceColor = article.content_type === 'academic' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className={`text-xs px-2 py-1 rounded-full ${sourceColor}`}>
                {article.source}
              </span>
              
              {article.content_type === 'academic' && (
                <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800">
                  學術論文
                </span>
              )}
              
              {article.content_type === 'news' && (
                <span className="text-xs px-2 py-1 rounded-full bg-orange-100 text-orange-800">
                  新聞
                </span>
              )}
            </div>
            
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              {article.title}
            </h2>
            
            <p className="text-gray-600 text-sm mb-4">
              {article.summary}
            </p>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={onPlay}
                className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                  isPlaying
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-primary-500 text-white hover:bg-primary-600'
                }`}
              >
                {isPlaying ? <FiPause className="mr-2" /> : <FiPlay className="mr-2" />}
                {isPlaying ? '暫停播放' : '播放摘要'}
              </button>
              
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200"
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