import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Compass, 
  Calendar, 
  Bookmark, 
  Bell, 
  Sliders, 
  Trophy,
  Download,
  Smartphone
} from 'lucide-react';

const navItems = [
  { path: '/', label: '대시보드', icon: LayoutDashboard },
  { path: '/contests', label: '공모전 탐색', icon: Compass },
  { path: '/calendar', label: '마감 캘린더', icon: Calendar },
  { path: '/bookmarks', label: '북마크', icon: Bookmark },
  { path: '/notifications', label: '알림 이력', icon: Bell },
  { path: '/preferences', label: '맞춤 설정', icon: Sliders },
];

const Sidebar = () => {
  const [installed, setInstalled] = useState(false);

  const handleInstallApp = async () => {
    if (window.deferredInstallPrompt) {
      window.deferredInstallPrompt.prompt();
      const { outcome } = await window.deferredInstallPrompt.userChoice;
      if (outcome === 'accepted') {
        setInstalled(true);
        window.deferredInstallPrompt = null;
      }
    } else {
      alert('이미 앱이 설치되어 있거나, 브라우저 주소창 우측의 [설치] 아이콘 또는 브라우저 메뉴(⋮)에서 [앱 설치]를 선택하세요.');
    }
  };

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between hidden md:flex shrink-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-100 gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-extrabold text-lg tracking-tight text-slate-900">ContestMate</h1>
            <p className="text-[11px] text-slate-400 font-medium -mt-1">맞춤 공모전 캘린더</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-600 font-bold shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info & PWA App Install */}
      <div className="p-4 space-y-3 border-t border-slate-100">
        {!installed && (
          <button
            onClick={handleInstallApp}
            className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 active:scale-98 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-500/20 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>앱으로 설치하기 (PWA)</span>
          </button>
        )}

        <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/60">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            수집 엔진 정상 동작 중
          </div>
          <p className="text-[11px] text-slate-500">
            위비티, 링커리어, 씽굿 200+ 실시간
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
