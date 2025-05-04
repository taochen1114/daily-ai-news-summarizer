import { useState, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import AudioPlayer from '../components/AudioPlayer';
import ArticleCard from '../components/ArticleCard';
import Header from '../components/Header';
import DateSelector from '../components/DateSelector';

// 定義類型
interface Source {
  name: string;
  count: number;
}

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

interface DailyReport {
  date: string;
  total_articles: number;
  sources: Source[];
  articles: Article[];
}

export default function Home() {
  const [dailyData, setDailyData] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);

  // 獲取可用日期
  useEffect(() => {
    const fetchDates = async () => {
      try {
        const response = await axios.get(`${process.env.API_URL}/dates`);
        setAvailableDates(response.data.dates || []);
        
        // 如果沒有選擇日期，預設選擇最新的
        if (!selectedDate && response.data.dates && response.data.dates.length > 0) {
          setSelectedDate(response.data.dates[0]);
        }
      } catch (err) {
        console.error('獲取日期失敗', err);
      }
    };
    
    fetchDates();
  }, [selectedDate]);

  // 獲取每日資料
  useEffect(() => {
    const fetchDailyData = async () => {
      if (!selectedDate) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get<DailyReport>(
          `${process.env.API_URL}/daily${selectedDate ? `?date=${selectedDate}` : ''}`
        );
        setDailyData(response.data);
      } catch (err: any) {
        console.error('獲取資料失敗', err);
        setError(err.response?.data?.detail || '載入資料時出錯');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDailyData();
  }, [selectedDate]);

  // 播放音訊
  const handlePlay = (articleId: string) => {
    if (currentPlayingId === articleId) {
      // 如果點擊的是當前正在播放的文章，則暫停
      setCurrentPlayingId(null);
    } else {
      // 否則播放新的文章
      setCurrentPlayingId(articleId);
    }
  };

  // 格式化日期顯示
  const formatDisplayDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return format(date, 'yyyy年MM月dd日 EEEE', { locale: zhTW });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <>
      <Head>
        <title>DAINS - 每日AI新聞和論文摘要</title>
        <meta name="description" content="每天追蹤AI新聞與論文，並生成語音摘要" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">每日AI新聞和論文摘要</h1>
              {dailyData && (
                <p className="text-gray-600 mt-2">
                  {formatDisplayDate(dailyData.date)} · 共 {dailyData.total_articles} 篇內容
                </p>
              )}
            </div>
            
            <DateSelector 
              dates={availableDates}
              selectedDate={selectedDate}
              onSelectDate={setSelectedDate}
            />
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : error ? (
            <div className="text-center py-10">
              <div className="text-red-500 text-lg">{error}</div>
              <button 
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600"
              >
                重試
              </button>
            </div>
          ) : dailyData ? (
            <div className="grid grid-cols-1 gap-6">
              {dailyData.articles.map((article) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  isPlaying={currentPlayingId === article.id}
                  onPlay={() => handlePlay(article.id)}
                />
              ))}
              
              {dailyData.articles.length === 0 && (
                <div className="text-center py-10 text-gray-500">
                  當天沒有內容
                </div>
              )}
            </div>
          ) : null}
        </main>
        
        {currentPlayingId && dailyData && (
          <AudioPlayer
            article={dailyData.articles.find(a => a.id === currentPlayingId)!}
            onClose={() => setCurrentPlayingId(null)}
          />
        )}
        
        <footer className="bg-white border-t border-gray-200 py-6">
          <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
            <p>DAINS - 每日AI新聞與論文摘要</p>
            <p className="mt-1">© {new Date().getFullYear()} DAINS 版權所有</p>
          </div>
        </footer>
      </div>
    </>
  );
} 