import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

const About = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>關於 - AI 新聞摘要</title>
        <meta name="description" content="AI 新聞摘要系統的關於頁面" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">關於 AI 新聞摘要</h1>
          
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">專案介紹</h2>
            <p className="text-gray-600 mb-4">
              AI 新聞摘要是一個自動化的新聞摘要系統，專門用於收集和整理 AI 相關的新聞和學術論文。
              系統會自動從多個來源（如 VentureBeat、ArXiv 等）抓取最新內容，並使用 AI 技術生成簡潔的摘要。
            </p>
            <p className="text-gray-600">
              我們的目標是幫助使用者快速掌握 AI 領域的最新動態，節省閱讀時間，提高資訊獲取效率。
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">主要功能</h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>自動抓取多個來源的 AI 相關新聞和論文</li>
              <li>使用 AI 技術生成簡潔的摘要</li>
              <li>支援文字轉語音功能，方便隨時收聽</li>
              <li>提供分類和搜尋功能，快速找到感興趣的內容</li>
              <li>定期更新，確保內容的新鮮度</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">技術架構</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-xl font-medium text-gray-700 mb-2">後端技術</h3>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Python FastAPI</li>
                  <li>SQLite 資料庫</li>
                  <li>OpenAI API</li>
                  <li>ElevenLabs TTS API</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-medium text-gray-700 mb-2">前端技術</h3>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Next.js</li>
                  <li>TypeScript</li>
                  <li>Tailwind CSS</li>
                  <li>React Query</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">資料來源</h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>VentureBeat AI 新聞</li>
              <li>ArXiv CS.AI 論文</li>
              <li>更多來源陸續添加中...</li>
            </ul>
          </div>

          <div className="flex justify-center mt-8">
            <Link href="/">
              <a className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300">
                返回首頁
              </a>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About; 