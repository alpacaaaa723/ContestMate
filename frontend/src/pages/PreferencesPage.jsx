import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Save, 
  Send, 
  Plus, 
  X, 
  CheckCircle2, 
  MessageSquare, 
  Sparkles,
  HelpCircle 
} from 'lucide-react';
import { preferenceApi, notificationApi } from '../services/api';

const availableCategories = [
  'IT / 개발',
  'AI / 인공지능',
  '기획 / 아이디어',
  '디자인',
  '마케팅',
  '영상 / 콘텐츠',
  '창업',
  '과학 / 기술',
  '기타'
];

const availableTargets = [
  '대학생',
  '대학원생',
  '일반인',
  '청소년',
  '직장인',
  '제한 없음'
];

const defaultKeywords = ['해커톤', 'AI', '대학생', '지원금', '개발', '창업'];

const PreferencesPage = () => {
  const [pref, setPref] = useState({
    categories: ['IT / 개발', 'AI / 인공지능'],
    keywords: ['해커톤', 'AI', '개발'],
    keyword_match_type: 'OR',
    target_types: ['대학생', '제한 없음'],
    hide_expired: false,
    notify_new_contests: true,
    notify_deadlines: true,
    telegram_chat_id: ''
  });

  const [customKeyword, setCustomKeyword] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingTelegram, setTestingTelegram] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  useEffect(() => {
    preferenceApi.getPreferences()
      .then(data => {
        if (data) setPref(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  const handleCategoryToggle = (cat) => {
    setPref(prev => {
      const exists = prev.categories.includes(cat);
      const nextCats = exists 
        ? prev.categories.filter(c => c !== cat)
        : [...prev.categories, cat];
      return { ...prev, categories: nextCats };
    });
  };

  const handleTargetToggle = (target) => {
    setPref(prev => {
      const exists = prev.target_types.includes(target);
      const nextTargets = exists 
        ? prev.target_types.filter(t => t !== target)
        : [...prev.target_types, target];
      return { ...prev, target_types: nextTargets };
    });
  };

  const addKeyword = (kw) => {
    const trimmed = kw.trim();
    if (!trimmed || pref.keywords.includes(trimmed)) return;
    setPref(prev => ({ ...prev, keywords: [...prev.keywords, trimmed] }));
    setCustomKeyword('');
  };

  const removeKeyword = (kw) => {
    setPref(prev => ({ ...prev, keywords: prev.keywords.filter(k => k !== kw) }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await preferenceApi.updatePreferences(pref);
      showToast('맞춤 설정이 안전하게 저장되었습니다!');
    } catch (err) {
      alert('저장 실패: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    if (!pref.telegram_chat_id) {
      alert('먼저 Telegram Chat ID를 입력해주세요.');
      return;
    }
    try {
      setTestingTelegram(true);
      await notificationApi.sendTest({ telegram_chat_id: pref.telegram_chat_id });
      showToast('텔레그램 테스트 메시지가 성공적으로 발송되었습니다!');
    } catch (err) {
      alert('발송 실패: ' + (err.response?.data?.detail || err.message));
    } finally {
      setTestingTelegram(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">설정 로딩 중...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-5 py-3 rounded-2xl shadow-xl flex items-center gap-2 text-sm font-semibold animate-slideUp">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">맞춤 설정 (Preferences)</h1>
        <p className="text-xs text-slate-500 mt-1">
          관심 분야, 필수 키워드, 참가 대상을 설정하여 최적화된 공모전을 추천받으세요.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* 1. 관심 분야 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">1</span>
            <h2 className="text-base font-bold text-slate-900">관심 분야 선택</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {availableCategories.map((cat) => {
              const active = pref.categories.includes(cat);
              return (
                <button
                  type="button"
                  key={cat}
                  onClick={() => handleCategoryToggle(cat)}
                  className={`px-4 py-2.5 rounded-2xl text-xs font-bold transition-all ${
                    active
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                      : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. 키워드 및 매칭 조건 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">2</span>
              <h2 className="text-base font-bold text-slate-900">맞춤 키워드 및 매칭 방식</h2>
            </div>
            
            {/* OR / AND Toggle */}
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
              <button
                type="button"
                onClick={() => setPref(p => ({ ...p, keyword_match_type: 'OR' }))}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  pref.keyword_match_type === 'OR'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500'
                }`}
              >
                OR 매칭 (추천)
              </button>
              <button
                type="button"
                onClick={() => setPref(p => ({ ...p, keyword_match_type: 'AND' }))}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  pref.keyword_match_type === 'AND'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500'
                }`}
              >
                AND 매칭 (엄격)
              </button>
            </div>
          </div>

          <p className="text-xs text-slate-500">
            {pref.keyword_match_type === 'OR' 
              ? '설정한 키워드 중 하나라도 포함되면 맞춤 추천 점수를 부여합니다.' 
              : '설정한 모든 키워드가 반드시 포함되어야만 추천 목록 상위에 노출됩니다.'}
          </p>

          {/* Keyword tags */}
          <div className="flex flex-wrap gap-2 items-center">
            {pref.keywords.map((kw) => (
              <span 
                key={kw}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold"
              >
                <span>#{kw}</span>
                <button
                  type="button"
                  onClick={() => removeKeyword(kw)}
                  className="p-0.5 hover:bg-blue-200 rounded-full"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>

          {/* Add Keyword input */}
          <div className="flex items-center gap-2 max-w-md pt-2">
            <input
              type="text"
              placeholder="자유 키워드 입력 (예: 해커톤, 장학금)..."
              value={customKeyword}
              onChange={(e) => setCustomKeyword(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addKeyword(customKeyword);
                }
              }}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-xs bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
            <button
              type="button"
              onClick={() => addKeyword(customKeyword)}
              className="px-4 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>추가</span>
            </button>
          </div>

          {/* Quick Recommend Keywords */}
          <div className="pt-2 flex items-center gap-2 flex-wrap text-xs text-slate-400">
            <span className="font-semibold text-slate-500">추천 키워드:</span>
            {defaultKeywords.map(k => (
              <button
                type="button"
                key={k}
                onClick={() => addKeyword(k)}
                className="px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 text-[11px]"
              >
                +{k}
              </button>
            ))}
          </div>
        </div>

        {/* 3. 참가 대상 및 필터 옵션 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">3</span>
            <h2 className="text-base font-bold text-slate-900">참가 대상 및 표시 옵션</h2>
          </div>

          <div className="flex flex-wrap gap-2">
            {availableTargets.map((target) => {
              const active = pref.target_types.includes(target);
              return (
                <button
                  type="button"
                  key={target}
                  onClick={() => handleTargetToggle(target)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                    active
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {target}
                </button>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-100">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={pref.hide_expired}
                onChange={(e) => setPref(p => ({ ...p, hide_expired: e.target.checked }))}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <span className="text-xs font-bold text-slate-700">마감된 공모전은 목록 및 추천에서 숨기기</span>
            </label>
          </div>
        </div>

        {/* 4. Telegram 알림 설정 */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">4</span>
            <h2 className="text-base font-bold text-slate-900">Telegram 알림 연동</h2>
          </div>

          <p className="text-xs text-slate-500">
            텔레그램 봇을 통해 신규 맞춤 공모전 및 마감 D-7, D-3, D-1, 당일 알림을 즉시 받아볼 수 있습니다.
          </p>

          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <input
                type="text"
                placeholder="Telegram Chat ID를 입력하세요 (예: 123456789)"
                value={pref.telegram_chat_id || ''}
                onChange={(e) => setPref(p => ({ ...p, telegram_chat_id: e.target.value }))}
                className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-xs bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <button
                type="button"
                onClick={handleTestTelegram}
                disabled={testingTelegram}
                className="px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 transition flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5 text-blue-600" />
                <span>{testingTelegram ? '발송 중...' : '연동 테스트 메시지'}</span>
              </button>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={pref.notify_deadlines}
                  onChange={(e) => setPref(p => ({ ...p, notify_deadlines: e.target.checked }))}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
                />
                <span className="text-xs font-semibold text-slate-700">마감 임박 알림 수신 (D-7, D-3, D-1, 당일)</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={pref.notify_new_contests}
                  onChange={(e) => setPref(p => ({ ...p, notify_new_contests: e.target.checked }))}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
                />
                <span className="text-xs font-semibold text-slate-700">신규 맞춤 공모전 등록 알림</span>
              </label>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-blue-600 text-white font-extrabold text-sm hover:bg-blue-700 transition shadow-lg shadow-blue-500/25 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? '저장 중...' : '맞춤 설정 저장하기'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default PreferencesPage;
