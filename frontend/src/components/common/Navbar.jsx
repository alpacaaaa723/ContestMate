import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { RefreshCw, Menu, Download } from 'lucide-react';
import { adminApi } from '../../services/api';

const Navbar = ({ onMobileMenuToggle }) => {
  const { user } = useAuth();
  const [collecting, setCollecting] = useState(false);

  const handleManualCollect = async () => {
    try {
      setCollecting(true);
      await adminApi.collectNow();
      alert('공모전 데이터 수집이 완료되었습니다. 페이지를 새로고침하면 최신 데이터가 반영됩니다.');
      window.location.reload();
    } catch (e) {
      alert('수집 요청 중 오류가 발생했습니다: ' + e.message);
    } finally {
      setCollecting(false);
    }
  };

  const handleInstallApp = async () => {
    if (window.deferredInstallPrompt) {
      window.deferredInstallPrompt.prompt();
      await window.deferredInstallPrompt.userChoice;
    } else {
      alert('브라우저 주소창 우측의 [설치] 버튼을 누르거나, 모바일에서는 [홈 화면에 추가]를 선택해주세요.');
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 md:px-8 flex items-center justify-between shrink-0 sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button 
          onClick={onMobileMenuToggle} 
          aria-label="메뉴 열기"
          className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="text-sm font-medium text-slate-500 hidden sm:block">
          대학생 & 취업준비생을 위한 스마트 공모전 파트너
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* 앱 설치 버튼 (헤더) */}
        <button
          onClick={handleInstallApp}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 border border-indigo-200/80 text-xs font-bold text-indigo-700 hover:bg-indigo-100 transition-colors shadow-sm"
          title="ContestMate 앱으로 설치"
        >
          <Download className="w-3.5 h-3.5 text-indigo-600" />
          <span>앱 설치</span>
        </button>

        {/* 온디맨드 수집 트리거 버튼 */}
        <button
          onClick={handleManualCollect}
          disabled={collecting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
          title="공모전 데이터 즉시 동기화"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${collecting ? 'animate-spin text-indigo-600' : ''}`} />
          <span className="hidden xs:inline">{collecting ? '수집 중...' : '데이터 동기화'}</span>
        </button>

        {/* 사용자 정보 */}
        <div className="flex items-center gap-2 pl-2 sm:pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
            {user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-bold text-slate-800">{user?.email?.split('@')[0]}</div>
            <div className="text-[10px] text-slate-400">맞춤 추천 활성화됨</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
