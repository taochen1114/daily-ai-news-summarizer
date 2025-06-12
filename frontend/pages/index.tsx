import { useState, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import AudioPlayer from '../components/AudioPlayer';
import ArticleCard from '../components/ArticleCard';
import Header from '../components/Header';
import DateSelector from '../components/DateSelector';
import { Article } from '../types';

// 定義類型
interface Source {
  name: string;
  count: number;
}

interface DailyReport {
  date: string;
  total_articles: number;
  sources: Source[];
  articles: Article[];
}

// 獲取今天的日期字串
const getTodayDate = (): string => {
  return format(new Date(), 'yyyy-MM-dd');
};

// 在獲取音訊文件時使用相對路徑
const getAudioUrl = (audioFile: string) => {
  return `/api/audio/${audioFile}`;
};

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(getTodayDate());
  const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);
  const [loadedDates, setLoadedDates] = useState<Set<string>>(
    new Set([getTodayDate()])
  );
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  // 添加文章緩存
  const [articlesCache, setArticlesCache] = useState<Record<string, Article[]>>(
    {}
  );

  // 獲取日期列表
  const fetchDates = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/dates`);
      if (!response.ok) throw new Error('獲取日期列表失敗');
      const data = await response.json();
      const dates = Array.isArray(data) ? data : data.dates || [];
      setAvailableDates(dates);
      return dates;
    } catch (error) {
      console.error('獲取日期列表時出錯:', error);
      setAvailableDates([]);
      return [];
    }
  };

  // 獲取指定日期的文章
  const fetchArticles = async (date: string) => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/daily?date=${date}`
      );
      if (!response.ok) throw new Error('獲取文章失敗');
      const data = await response.json();
      const articles = data.articles || [];
      // 更新緩存
      setArticlesCache((prev) => ({
        ...prev,
        [date]: articles,
      }));
      return articles;
    } catch (error) {
      console.error('獲取文章時出錯:', error);
      return [];
    } finally {
      setLoading(false);
    }
  };

  // 獲取最近的日期
  const getLatestDate = (dates: string[]): string => {
    if (!dates.length) return getTodayDate();

    // 將日期字串轉換為 Date 對象並排序
    const sortedDates = dates
      .map((date) => new Date(date))
      .sort((a, b) => b.getTime() - a.getTime());

    // 返回最近的日期字串
    return format(sortedDates[0], 'yyyy-MM-dd');
  };

  // 初始加載最新日期的文章和日期列表
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        // 先獲取日期列表
        const dates = await fetchDates();
        // 獲取最近的日期
        const latestDate = getLatestDate(dates);
        // 加載最近日期的文章
        const articles = await fetchArticles(latestDate);

        setArticles(articles);
        setSelectedDate(latestDate);
        setAvailableDates(dates);
        // 初始化緩存
        setArticlesCache({ [latestDate]: articles });
        // 更新已加載日期集合
        setLoadedDates(new Set([latestDate]));
      } catch (error) {
        setError('加載文章時出錯');
        console.error('加載文章時出錯:', error);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // 處理日期切換
  const handleDateChange = async (date: string) => {
    setSelectedDate(date);
    setCurrentPlayingId(null);

    // 如果該日期的文章已經在緩存中，直接使用
    if (articlesCache[date]) {
      setArticles(articlesCache[date]);
      return;
    }

    // 如果該日期的文章尚未加載，則加載它
    if (!loadedDates.has(date)) {
      try {
        setLoading(true);
        const data = await fetchArticles(date);
        setArticles(data);
        setLoadedDates(new Set([...Array.from(loadedDates), date]));
      } catch (error) {
        setError('加載文章時出錯');
        console.error('加載文章時出錯:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // 處理播放
  const handlePlay = (article: Article) => {
    if (currentPlayingId === article.id) {
      setCurrentPlayingId(null);
    } else {
      setCurrentPlayingId(article.id);
    }
  };

  // 獲取當前播放的文章
  const currentPlayingArticle = articles.find(
    (article) => article.id === currentPlayingId
  );

  return (
    <>
      <Head>
        <title>DAINS - 每日AI新聞和論文摘要</title>
        <meta
          name="description"
          content="每天追蹤AI新聞與論文，並生成語音摘要"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <Header />

        <main className="container mx-auto px-4 py-8">
          <div className="mb-8 flex flex-col items-start justify-between md:flex-row md:items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                每日AI新聞和論文摘要
              </h1>
              {articles.length > 0 && (
                <p className="mt-2 text-gray-600">
                  {format(
                    new Date(articles[0].published_date || ''),
                    'yyyy年MM月dd日 EEEE',
                    { locale: zhTW }
                  )}{' '}
                  · 共 {articles.length} 篇內容
                </p>
              )}
            </div>

            <DateSelector
              dates={availableDates}
              selectedDate={selectedDate}
              onSelectDate={handleDateChange}
            />
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-primary-500"></div>
            </div>
          ) : error ? (
            <div className="py-10 text-center">
              <div className="text-lg text-red-500">{error}</div>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 rounded bg-primary-500 px-4 py-2 text-white hover:bg-primary-600"
              >
                重試
              </button>
            </div>
          ) : articles.length > 0 ? (
            <div className="grid grid-cols-1 gap-6">
              {articles.map((article) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  isPlaying={currentPlayingId === article.id}
                  onPlay={() => handlePlay(article)}
                />
              ))}

              {articles.length === 0 && (
                <div className="py-10 text-center text-gray-500">
                  當天沒有內容
                </div>
              )}
            </div>
          ) : null}
        </main>

        {currentPlayingArticle && (
          <AudioPlayer
            article={currentPlayingArticle}
            onClose={() => setCurrentPlayingId(null)}
          />
        )}

        <footer className="border-t border-gray-200 bg-white py-6">
          <div className="container mx-auto px-4 text-center text-sm text-gray-500">
            <p>DAINS - 每日AI新聞與論文摘要</p>
            <p className="mt-1">© {new Date().getFullYear()} DAINS 版權所有</p>
          </div>
        </footer>
      </div>
    </>
  );
}
