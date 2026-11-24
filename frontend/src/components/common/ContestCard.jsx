import React, { useState, useEffect } from 'react';
import { Bookmark, ExternalLink, Calendar, Building, Sparkles } from 'lucide-react';
import DDayBadge from './DDayBadge';
import { bookmarkApi } from '../../services/api';

const getSourceColor = (source) => {
  switch (source) {
    case '위비티': return 'bg-orange-50 text-orange-700 border-orange-200';
    case '씽굿': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case '링커리어': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
    default: return 'bg-slate-50 text-slate-700 border-slate-200';
  }
};

const ContestCard = ({ contest, onSelect, onBookmarkChanged }) => {
  const [isBookmarked, setIsBookmarked] = useState(Boolean(contest.is_bookmarked));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setIsBookmarked(Boolean(contest.is_bookmarked));
  }, [contest.is_bookmarked, contest.id]);

  const toggleBookmark = async (e) => {
    e.stopPropagation();
    if (loading) return;
    try {
      setLoading(true);
      if (isBookmarked) {
        await bookmarkApi.removeBookmark(contest.id);
        setIsBookmarked(false);
        if (onBookmarkChanged) onBookmarkChanged(contest.id, false);
      } else {
        await bookmarkApi.addBookmark(contest.id);
        setIsBookmarked(true);
        if (onBookmarkChanged) onBookmarkChanged(contest.id, true);
      }
    } catch (err) {
      alert('북마크 변경 실패: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      onClick={() => onSelect && onSelect(contest)}
      className="bg-white rounded-2xl border border-slate-200/80 p-5 hover:shadow-lg hover:border-blue-300 transition-all cursor-pointer flex flex-col justify-between group relative"
    >
      <div>
        {/* Header Tags */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${getSourceColor(contest.source)}`}>
              {contest.source}
            </span>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
              {contest.category}
            </span>
            <DDayBadge dday={contest.dday} />
          </div>

          {/* Bookmark Button */}
          <button
            onClick={toggleBookmark}
            disabled={loading}
            className={`p-1.5 rounded-lg border transition-all ${
              isBookmarked
                ? 'bg-amber-50 border-amber-300 text-amber-500 fill-amber-500 shadow-sm'
                : 'border-slate-200 text-slate-400 hover:text-slate-600 hover:bg-slate-50'
            }`}
            title={isBookmarked ? '북마크 해제' : '북마크 저장'}
          >
            <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
          </button>
        </div>

        {/* Title */}
        <h3 className="font-bold text-slate-900 text-base leading-snug group-hover:text-blue-600 transition-colors line-clamp-2 mb-2">
          {contest.title}
        </h3>

        {/* Organizer & Meta */}
        <div className="space-y-1.5 text-xs text-slate-500 mb-4">
          <div className="flex items-center gap-1.5">
            <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{contest.organizer}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>접수 마감: {contest.end_date}</span>
          </div>
        </div>

        {/* Matched Reasons Tag */}
        {contest.matched_reasons && contest.matched_reasons.length > 0 && (
          <div className="mb-4 bg-blue-50/70 border border-blue-100 rounded-xl p-2.5">
            <div className="flex items-center gap-1 text-[11px] font-bold text-blue-700 mb-1">
              <Sparkles className="w-3 h-3 text-blue-600" />
              <span>맞춤 추천 이유</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {contest.matched_reasons.map((reason, idx) => (
                <span key={idx} className="text-[10px] bg-white text-blue-800 px-1.5 py-0.5 rounded border border-blue-200 font-medium">
                  {reason}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Info & Actions */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="text-slate-500 font-medium truncate max-w-[150px]">
          {contest.prize || '시상내역 공고 참조'}
        </span>
        <a
          href={contest.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800"
        >
          <span>원문 공고</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};

export default ContestCard;
