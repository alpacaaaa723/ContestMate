import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Bookmark, Building, Calendar, Award, Users, Tag } from 'lucide-react';
import DDayBadge from './DDayBadge';
import { bookmarkApi } from '../../services/api';

const ContestDetailModal = ({ contest, isOpen, onClose, onBookmarkChanged }) => {
  const [isBookmarked, setIsBookmarked] = useState(Boolean(contest?.is_bookmarked));
  const [bookmarkLoading, setBookmarkLoading] = useState(false);

  useEffect(() => {
    setIsBookmarked(Boolean(contest?.is_bookmarked));
  }, [contest?.is_bookmarked, contest?.id]);

  if (!isOpen || !contest) return null;

  const handleToggleBookmark = async () => {
    if (bookmarkLoading || !contest?.id) return;
    try {
      setBookmarkLoading(true);
      if (isBookmarked) {
        await bookmarkApi.removeBookmark(contest.id);
        setIsBookmarked(false);
        if (onBookmarkChanged) onBookmarkChanged(contest.id, false);
      } else {
        await bookmarkApi.addBookmark(contest.id);
        setIsBookmarked(true);
        if (onBookmarkChanged) onBookmarkChanged(contest.id, true);
      }
    } catch (e) {
      alert('북마크 변경 실패: ' + e.message);
    } finally {
      setBookmarkLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
      <div 
        className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-start justify-between gap-4 sticky top-0 bg-white/95 backdrop-blur z-10">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-blue-100 text-blue-800">
                {contest.source}
              </span>
              <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                {contest.category}
              </span>
              <DDayBadge dday={contest.dday} />
            </div>
            <h2 className="text-xl font-extrabold text-slate-900 leading-snug">
              {contest.title}
            </h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 text-sm text-slate-600">
          {/* Key Facts Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-200/60">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white shadow-sm border border-slate-200 text-blue-600">
                <Building className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium">주최기관</p>
                <p className="font-bold text-slate-800">{contest.organizer}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white shadow-sm border border-slate-200 text-rose-600">
                <Calendar className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium">접수 마감일</p>
                <p className="font-bold text-slate-800">{contest.end_date}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white shadow-sm border border-slate-200 text-amber-600">
                <Users className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium">참가 대상</p>
                <p className="font-bold text-slate-800">{contest.target_type || '제한없음'}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white shadow-sm border border-slate-200 text-emerald-600">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium">시상 및 혜택</p>
                <p className="font-bold text-slate-800">{contest.prize || '상세 공고 참조'}</p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="font-bold text-slate-900 mb-2">공모전 상세 설명</h3>
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/60 leading-relaxed whitespace-pre-line text-slate-700">
              {contest.description || '상세 설명은 원문 공고 페이지를 확인해 주세요.'}
            </div>
          </div>

          {/* Matching Reasons */}
          {contest.matched_reasons && contest.matched_reasons.length > 0 && (
            <div className="bg-blue-50/60 border border-blue-200 rounded-2xl p-4">
              <h3 className="font-bold text-blue-900 text-xs mb-2 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-blue-600" />
                사용자 맞춤 조건 일치 내역
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {contest.matched_reasons.map((r, i) => (
                  <span key={i} className="text-xs bg-white text-blue-700 px-2 py-1 rounded-lg border border-blue-200 font-semibold">
                    {r}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-6 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
          <button
            onClick={handleToggleBookmark}
            disabled={bookmarkLoading}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border text-xs sm:text-sm font-bold transition shadow-sm ${
              isBookmarked
                ? 'bg-amber-50 border-amber-300 text-amber-700 shadow-amber-500/10'
                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : 'text-slate-400'}`} />
            <span>{isBookmarked ? '북마크 저장됨' : '북마크 추가'}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm font-semibold text-slate-600 hover:bg-slate-100"
            >
              닫기
            </button>
            <a
              href={contest.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-600 text-white text-xs sm:text-sm font-bold hover:bg-blue-700 transition shadow-md shadow-blue-500/20"
            >
              <span>원본 공고 이동</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContestDetailModal;
