import React from 'react';
import Link from 'next/link';
import ThemeToggle from './ThemeToggle';
import { FiDatabase, FiGithub, FiInfo } from 'react-icons/fi';

const Header: React.FC = () => {
  return (
    <header className="border-b border-gray-200 py-4 dark:border-gray-700">
      <div className="container mx-auto flex flex-col items-center justify-between px-4 md:flex-row">
        <div className="mb-4 flex items-center md:mb-0">
          <Link
            href="/"
            className="flex items-center text-2xl font-bold text-primary-600 dark:text-primary-400"
          >
            <FiDatabase className="mr-2" />
            DAINS
          </Link>
          <span className="ml-4 hidden text-sm text-gray-600 md:inline dark:text-gray-400">
            每日AI新聞和論文摘要
          </span>
        </div>

        <div className="flex items-center space-x-6">
          <Link
            href="/about"
            className="flex items-center text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400"
          >
            <FiInfo className="mr-1" />
            <span>關於</span>
          </Link>
          <a
            href="https://github.com/taochen1114/daily-ai-news-summarizer"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400"
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
