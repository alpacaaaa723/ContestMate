import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Trophy, 
  Sparkles, 
  Bookmark, 
  Clock, 
  ArrowRight, 
  Calendar,
  AlertCircle 
} from 'lucide-react';
import { contestApi, bookmarkApi } from '../services/api';
import ContestCard from '../components/common/ContestCard';
import ContestDetailModal from '../components/common/ContestDetailModal';

const DashboardPage = () => {
  const [stats, setStats] = useState({
    total: 0,
    recommended: 0,
    bookmarked: 0,
    urgent: 0
  });
  const [recommendedContests, setRecommendedContests] = useState([]);
  const [urgentContests, setUrgentContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContest, setSelectedContest] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [allRes, recRes, bmRes] = await Promise.all([
        contestApi.getContests({ page_size: 100 }),
        contestApi.getRecommended(6),
        bookmarkApi.getBookmarks()
      ]);

      const items = Array.isArray(allRes?.items) ? allRes.items : [];
      const recList = Array.isArray(recRes) ? recRes : [];
      const bmList = Array.isArray(bmRes) ? bmRes : [];
      const urgentList = items.filter(c => c.dday >= 0 && c.dday <= 3);

      setStats({
        total: allRes?.total || items.length,
        recommended: recList.length,
        bookmarked: bmList.length,
        urgent: urgentList.length
      });

      setRecommendedContests(recList);
      setUrgentContests(urgentList.slice(0, 4));
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-blue-500/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            AI 기반 맞춤 공모전 큐레이션
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            오늘도 새로운 기회에 도전해보세요!
          </h1>
          <p className="text-blue-100 text-sm mt-2 max-w-xl">
            위비티, 링커리어, 캠퍼스픽, 올콘, 콘테스트코리아, 데브이벤트 등 국내 주요 공모전 포털의 500여 개 대회를 종합 분석하여 회원님의 관심 분야와 참가 조건에 맞는 공모전만 골라 추천해드립니다.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <Link
            to="/calendar"
            className="px-5 py-3 rounded-2xl bg-white text-blue-700 font-bold text-sm hover:bg-blue-50 transition shadow-sm flex items-center gap-2"
          >
            <Calendar className="w-4 h-4" />
            <span>마감 캘린더</span>
          </Link>
          <Link
            to="/contests"
            className="px-5 py-3 rounded-2xl bg-blue-800/80 hover:bg-blue-800 text-white font-bold text-sm transition border border-white/20 flex items-center gap-2"
          >
            <span>전체 탐색</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400">전체 공모전</p>
            <h3 className="text-2xl font-black text-slate-900 mt-0.5">{stats.total}개</h3>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400">맞춤 추천</p>
            <h3 className="text-2xl font-black text-indigo-600 mt-0.5">{stats.recommended}개</h3>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-500 flex items-center justify-center shrink-0">
            <Bookmark className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400">북마크 저장</p>
            <h3 className="text-2xl font-black text-slate-900 mt-0.5">{stats.bookmarked}개</h3>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400">마감 임박 (D-3)</p>
            <h3 className="text-2xl font-black text-rose-600 mt-0.5">{stats.urgent}개</h3>
          </div>
        </div>
      </div>

      {/* Recommended Contests Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-slate-900">맞춤 추천 공모전</h2>
          </div>
          <Link to="/contests?sort_by=interest" className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1">
            <span>더보기</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(n => (
              <div key={n} className="h-64 rounded-2xl bg-slate-200/70 animate-pulse"></div>
            ))}
          </div>
        ) : recommendedContests.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendedContests.map(contest => (
              <ContestCard
                key={contest.id}
                contest={contest}
                onSelect={setSelectedContest}
                onBookmarkChanged={fetchDashboardData}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-8 text-center border border-slate-200 text-slate-500">
            맞춤 추천 공모전이 없습니다. [맞춤 설정]에서 관심 키워드를 등록해보세요.
          </div>
        )}
      </section>

      {/* Urgent Contests Section */}
      {urgentContests.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-600" />
              <h2 className="text-xl font-bold text-slate-900">곧 마감되는 공모전</h2>
            </div>
            <Link to="/calendar" className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1">
              <span>캘린더에서 보기</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {urgentContests.map(contest => (
              <ContestCard
                key={contest.id}
                contest={contest}
                onSelect={setSelectedContest}
                onBookmarkChanged={fetchDashboardData}
              />
            ))}
          </div>
        </section>
      )}

      {/* Modal */}
      <ContestDetailModal
        contest={selectedContest}
        isOpen={!!selectedContest}
        onClose={() => setSelectedContest(null)}
        onBookmarkChanged={fetchDashboardData}
      />
    </div>
  );
};

export default DashboardPage;
