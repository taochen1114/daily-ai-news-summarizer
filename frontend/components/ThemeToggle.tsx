import React from 'react';
import { FiSun, FiMoon } from 'react-icons/fi';

const ThemeToggle: React.FC = () => {
  // 由於這是一個範例元件，實際上不會運作
  // 在實際應用中，應該使用 useState 跟 useEffect 與本地儲存整合
  const toggleTheme = () => {
    console.log('切換主題');
  };

  return (
    <button
      onClick={toggleTheme}
      className="rounded-md bg-gray-100 p-2 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
      aria-label="切換明亮/暗黑模式"
    >
      <FiMoon className="hidden dark:block" />
      <FiSun className="block dark:hidden" />
    </button>
  );
};

export default ThemeToggle;
