import React from 'react';
import Link from 'next/link';
import ThemeToggle from './ThemeToggle';
import { FiDatabase, FiGithub, FiInfo } from 'react-icons/fi';

const Header: React.FC = () => {
  return (
    <header className="py-4 border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between">
        <div className="flex items-center mb-4 md:mb-0">
          <Link href="/" className="text-2xl font-bold text-primary-600 dark:text-primary-400 flex items-center">
            <FiDatabase className="mr-2" />
            DAINS
          </Link>
          <span className="text-sm text-gray-600 dark:text-gray-400 ml-4 hidden md:inline">
            每日AI新聞和論文摘要
          </span>
        </div>

        <div className="flex items-center space-x-6">
          <Link
            href="/about"
            className="text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400 flex items-center"
          >
            <FiInfo className="mr-1" />
            <span>關於</span>
          </Link>
          <a
            href="https://github.com/taochen1114/daily-ai-news-summarizer"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400 flex items-center"
          >
            <FiGithub className="mr-1" />
            <span>GitHub</span>
          </a>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default Header; 