import React, { useState, useRef, useEffect } from 'react';
import { FiX, FiPlay, FiPause, FiVolume2, FiVolumeX } from 'react-icons/fi';

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

interface AudioPlayerProps {
  article: Article;
  onClose: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ article, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  // 获取音频URL
  const audioUrl = `${process.env.API_URL}/audio/${article.id}`;

  // 播放暂停
  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  // 静音
  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  // 更新进度
  const handleTimeUpdate = () => {
    const audio = audioRef.current;
    if (!audio) return;

    setCurrentTime(audio.currentTime);
  };

  // 设置进度
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  // 加载完成时设置时长
  const handleLoadedMetadata = () => {
    const audio = audioRef.current;
    if (!audio) return;

    setDuration(audio.duration);
  };

  // 播放结束时重置
  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  };

  // 格式化时间显示
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  // 自动播放
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    try {
      audio.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error('自动播放失败:', err);
        setIsPlaying(false);
      });
    } catch (err) {
      console.error('播放出错:', err);
      setIsPlaying(false);
    }

    return () => {
      audio.pause();
    };
  }, []);

  return (
    <div className="fixed bottom-0 left-0 w-full bg-white shadow-lg border-t border-gray-200 z-50">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        hidden
      />

      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex-1 mr-4 truncate">
            <div className="text-sm font-medium text-gray-800 truncate">{article.title}</div>
            <div className="text-xs text-gray-500">{article.source}</div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlay}
              className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center hover:bg-primary-600"
            >
              {isPlaying ? <FiPause size={18} /> : <FiPlay size={18} />}
            </button>

            <div className="hidden md:flex items-center space-x-2 flex-1 max-w-md">
              <span className="text-xs text-gray-500 w-10 text-right">
                {formatTime(currentTime)}
              </span>
              <input
                type="range"
                min="0"
                max={duration || 0}
                value={currentTime}
                onChange={handleSeek}
                className="flex-1 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs text-gray-500 w-10">
                {formatTime(duration)}
              </span>
            </div>

            <button
              onClick={toggleMute}
              className="text-gray-500 hover:text-gray-700"
            >
              {isMuted ? <FiVolumeX size={20} /> : <FiVolume2 size={20} />}
            </button>

            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <FiX size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer; 