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
      className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
      aria-label="切換明亮/暗黑模式"
    >
      <FiMoon className="hidden dark:block" />
      <FiSun className="block dark:hidden" />
    </button>
  );
};

export default ThemeToggle; 