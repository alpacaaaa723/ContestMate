import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone, CheckCircle, Share2, PlusSquare } from 'lucide-react';

export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const [showIOSModal, setShowIOSModal] = useState(false);

  useEffect(() => {
    // 1. 이미 PWA standalone 모드로 실행 중인지 확인
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true;
    if (isStandalone) {
      setIsInstalled(true);
      return;
    }

    // 2. iOS Safari 감지
    const userAgent = window.navigator.userAgent.toLowerCase();
    const isIosDevice = /iphone|ipad|ipod/.test(userAgent);
    const isSafari = /safari/.test(userAgent) && !/chrome|crios|fxios/.test(userAgent);
    if (isIosDevice && isSafari) {
      setIsIOS(true);
      // 로컬 스토리지에 이전에 닫은 적이 없다면 표시
      const dismissed = localStorage.getItem('contestmate_ios_prompt_dismissed');
      if (!dismissed) {
        setShowBanner(true);
      }
    }

    // 3. Chrome / Edge / Android 네이티브 PWA 설치 이벤트 감지
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      // 전역 window 객체에도 보관하여 헤더/사이드바 버튼에서도 호출 가능하게 함
      window.deferredInstallPrompt = e;
      setShowBanner(true);
    };

    const handleAppInstalled = () => {
      console.log('[ContestMate] PWA installed successfully');
      setIsInstalled(true);
      setShowBanner(false);
      setDeferredPrompt(null);
      window.deferredInstallPrompt = null;
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (isIOS) {
      setShowIOSModal(true);
      return;
    }

    const promptEvent = deferredPrompt || window.deferredInstallPrompt;
    if (!promptEvent) {
      alert('이미 앱이 설치되어 있거나 브라우저 메뉴(⋮)에서 [앱 설치] 또는 [홈 화면에 추가]를 선택해주세요.');
      return;
    }

    promptEvent.prompt();
    const { outcome } = await promptEvent.userChoice;
    console.log(`[ContestMate] Install prompt outcome: ${outcome}`);
    if (outcome === 'accepted') {
      setShowBanner(false);
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    if (isIOS) {
      localStorage.setItem('contestmate_ios_prompt_dismissed', 'true');
    }
  };

  if (isInstalled || !showBanner) return null;

  return (
    <>
      {/* 하단 고정 플로팅 앱 설치 배너 */}
      <aside aria-label="앱 설치 안내" className="fixed bottom-20 md:bottom-4 left-4 right-4 md:left-auto md:right-6 md:w-96 z-40 animate-bounce-once">
        <div className="bg-slate-900 text-white p-4 rounded-2xl shadow-2xl border border-indigo-500/30 backdrop-blur-lg flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 p-0.5 shadow-md flex-shrink-0 flex items-center justify-center">
              <img src="/icons/icon-192.png" alt="ContestMate" className="w-10 h-10 rounded-lg object-cover" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-white flex items-center gap-1.5">
                ContestMate 앱 설치
                <span className="text-[10px] bg-indigo-500/30 text-indigo-300 font-medium px-1.5 py-0.5 rounded-full border border-indigo-400/30">PWA</span>
              </h4>
              <p className="text-xs text-slate-300 mt-0.5">
                바탕화면 / 홈 화면에 앱으로 추가하고 마감 알림을 받으세요!
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={handleInstallClick}
              className="bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all text-white font-semibold text-xs px-3.5 py-2 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              설치
            </button>
            <button
              onClick={handleDismiss}
              aria-label="닫기"
              className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* iOS Safari 전용 홈 화면 추가 안내 모달 */}
      {showIOSModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full text-slate-900 shadow-2xl animate-in slide-in-from-bottom">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold">
                  🏆
                </div>
                <h3 className="font-bold text-base">아이폰에서 앱 설치하기</h3>
              </div>
              <button onClick={() => setShowIOSModal(false)} aria-label="닫기" className="text-slate-400 hover:text-slate-600 p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <ol className="space-y-4 text-sm text-slate-600 mb-6">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center flex-shrink-0 text-xs">1</span>
                <div>
                  Safari 하단 메뉴바의 <span className="font-bold text-slate-900 inline-flex items-center gap-1"><Share2 className="w-3.5 h-3.5 inline text-indigo-600" /> 공유</span> 버튼을 터치합니다.
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center flex-shrink-0 text-xs">2</span>
                <div>
                  메뉴를 아래로 스크롤하여 <span className="font-bold text-slate-900 inline-flex items-center gap-1"><PlusSquare className="w-3.5 h-3.5 inline text-indigo-600" /> 홈 화면에 추가</span>를 선택합니다.
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center flex-shrink-0 text-xs">3</span>
                <div>
                  우측 상단의 <span className="font-bold text-indigo-600">추가</span>를 누르면 홈 화면에 앱 아이콘이 생성됩니다!
                </div>
              </li>
            </ol>

            <button
              onClick={() => setShowIOSModal(false)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors"
            >
              확인했습니다
            </button>
          </div>
        </div>
      )}
    </>
  );
}
