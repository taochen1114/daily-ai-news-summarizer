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

  // 設定音訊檔 URL
  let audioUrl;
  if (article.audio_file.startsWith('audio/articles')) {
    audioUrl = `${process.env.NEXT_PUBLIC_SUPABASE_STORAGE_URL}/${article.audio_file}`;
  } else {
    audioUrl = `${process.env.NEXT_PUBLIC_API_URL}/audio/${article.id}`;
  }

  // 播放暂停
  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio
        .play()
        .then(() => {
          setIsPlaying(true);
        })
        .catch((err) => {
          console.error('播放失败:', err);
          setIsPlaying(false);
        });
    }
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

    // 重置音頻狀態
    audio.pause();
    audio.currentTime = 0;
    setCurrentTime(0);
    setIsPlaying(false);

    // 設置新的音頻源
    audio.src = audioUrl;

    // 開始新的播放
    const playNewAudio = () => {
      audio
        .play()
        .then(() => {
          setIsPlaying(true);
        })
        .catch((err) => {
          console.error('播放失敗:', err);
          setIsPlaying(false);
        });
    };

    // 等待音頻加載完成後播放
    audio.addEventListener('loadeddata', playNewAudio);

    return () => {
      audio.removeEventListener('loadeddata', playNewAudio);
      audio.pause();
    };
  }, [article.id, audioUrl]);

  return (
    <div className="fixed bottom-0 left-0 z-50 w-full border-t border-gray-200 bg-white shadow-lg">
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
          <div className="mr-4 flex-1 truncate">
            <div className="truncate text-sm font-medium text-gray-800">
              {article.title}
            </div>
            <div className="text-xs text-gray-500">{article.source}</div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlay}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-white hover:bg-primary-600"
            >
              {isPlaying ? <FiPause size={18} /> : <FiPlay size={18} />}
            </button>

            <div className="hidden max-w-md flex-1 items-center space-x-2 md:flex">
              <span className="w-10 text-right text-xs text-gray-500">
                {formatTime(currentTime)}
              </span>
              <input
                type="range"
                min="0"
                max={duration || 0}
                value={currentTime}
                onChange={handleSeek}
                className="h-1 flex-1 cursor-pointer appearance-none rounded-lg bg-gray-200"
              />
              <span className="w-10 text-xs text-gray-500">
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
