import React from 'react';

const DDayBadge = ({ dday, className = '' }) => {
  let label = '';
  let colorClasses = '';

  if (dday < 0) {
    label = `마감 완료 (D+${Math.abs(dday)})`;
    colorClasses = 'bg-slate-100 text-slate-500 border-slate-300';
  } else if (dday === 0) {
    label = '🚨 오늘 마감 (D-Day)';
    colorClasses = 'bg-red-600 text-white border-red-700 animate-pulse font-bold shadow-sm';
  } else if (dday <= 2) {
    label = `🔥 D-${dday} (마감 임박)`;
    colorClasses = 'bg-rose-500 text-white border-rose-600 font-semibold';
  } else if (dday <= 6) {
    label = `⚠️ D-${dday} (주의)`;
    colorClasses = 'bg-amber-100 text-amber-800 border-amber-300 font-medium';
  } else {
    label = `D-${dday}`;
    colorClasses = 'bg-blue-50 text-blue-700 border-blue-200 font-medium';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${colorClasses} ${className}`}>
      {label}
    </span>
  );
};

export default DDayBadge;
