import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Compass, Calendar, Bookmark, Sliders } from 'lucide-react';

const navItems = [
  { path: '/', label: '홈', icon: LayoutDashboard },
  { path: '/contests', label: '탐색', icon: Compass },
  { path: '/calendar', label: '캘린더', icon: Calendar },
  { path: '/bookmarks', label: '북마크', icon: Bookmark },
  { path: '/preferences', label: '설정', icon: Sliders },
];

export default function BottomNav() {
  return (
    <nav 
      aria-label="모바일 하단 내비게이션"
      className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1 flex items-center justify-around shadow-lg"
    >
      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all ${
                isActive
                  ? 'text-indigo-600 font-bold'
                  : 'text-slate-500 hover:text-slate-900 font-medium'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`p-1 rounded-lg transition-transform ${isActive ? 'scale-110 bg-indigo-50' : ''}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-[10px] mt-0.5 tracking-tight">{item.label}</span>
              </>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
}
