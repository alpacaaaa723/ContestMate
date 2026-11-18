import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Calendar, ArrowRight, AlertCircle, Trash2 } from 'lucide-react';
import { bookmarkApi } from '../services/api';
import ContestCard from '../components/common/ContestCard';
import ContestDetailModal from '../components/common/ContestDetailModal';

const BookmarksPage = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContest, setSelectedContest] = useState(null);

  const fetchBookmarks = async () => {
    try {
      setLoading(true);
      const data = await bookmarkApi.getBookmarks();
      setBookmarks(data);
    } catch (err) {
      console.error('Failed to load bookmarks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookmarks();
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">관심 공모전 북마크</h1>
          <p className="text-xs text-slate-500 mt-1">
            저장해 둔 <span className="font-bold text-amber-500">{bookmarks.length}개</span>의 공모전을 마감 일정과 함께 관리하세요.
          </p>
        </div>

        <Link
          to="/calendar?filter=bookmark"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 text-white font-bold text-xs hover:bg-amber-600 transition shadow-md shadow-amber-500/20"
        >
          <Calendar className="w-4 h-4" />
          <span>캘린더에서 보기</span>
        </Link>
      </div>

      {/* Bookmarks List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(n => (
            <div key={n} className="h-64 rounded-2xl bg-slate-200/70 animate-pulse"></div>
          ))}
        </div>
      ) : bookmarks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {bookmarks.map((bm) => {
            const contest = bm.contest || { id: bm.contest_id, title: '공모전 정보 로딩...' };
            return (
              <ContestCard
                key={bm.id}
                contest={contest}
                onSelect={setSelectedContest}
                onBookmarkChanged={fetchBookmarks}
              />
            );
          })}
        </div>
      ) : (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-4">
          <div className="w-16 h-16 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center mx-auto">
            <Bookmark className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800">아직 저장한 북마크가 없습니다</h3>
            <p className="text-xs text-slate-500 mt-1">
              관심 있는 공모전의 북마크 아이콘을 눌러 저장하면 이곳과 캘린더에서 모아볼 수 있습니다.
            </p>
          </div>
          <Link
            to="/contests"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition"
          >
            <span>공모전 탐색하러 가기</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Modal */}
      <ContestDetailModal
        contest={selectedContest}
        isOpen={!!selectedContest}
        onClose={() => setSelectedContest(null)}
        onBookmarkChanged={fetchBookmarks}
      />
    </div>
  );
};

export default BookmarksPage;
