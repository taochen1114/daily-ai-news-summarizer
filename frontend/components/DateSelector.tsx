import React from 'react';
import { format, parseISO } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import { FiCalendar } from 'react-icons/fi';

interface DateSelectorProps {
  dates: string[];
  selectedDate: string | null;
  onSelectDate: (date: string) => void;
}

const DateSelector: React.FC<DateSelectorProps> = ({
  dates,
  selectedDate,
  onSelectDate,
}) => {
  const formatDate = (dateStr: string) => {
    try {
      return format(parseISO(dateStr), 'yyyy年MM月dd日', { locale: zhTW });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div className="mt-4 md:mt-0">
      <div className="relative">
        <select
          value={selectedDate || ''}
          onChange={(e) => onSelectDate(e.target.value)}
          className="cursor-pointer appearance-none rounded-md border border-gray-300 bg-white py-2 pl-10 pr-10 text-gray-700 hover:border-primary-500 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {dates.length === 0 ? (
            <option value="">載入中...</option>
          ) : (
            dates.map((date) => (
              <option key={date} value={date}>
                {formatDate(date)}
              </option>
            ))
          )}
        </select>
        <FiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 transform text-gray-500" />
      </div>
    </div>
  );
};

export default DateSelector;
