import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, ArrowUpDown, RefreshCw, AlertCircle } from 'lucide-react';
import { contestApi } from '../services/api';
import ContestCard from '../components/common/ContestCard';
import ContestDetailModal from '../components/common/ContestDetailModal';

const categories = [
  '전체',
  'IT / 개발',
  'AI / 인공지능',
  '기획 / 아이디어',
  '디자인',
  '마케팅',
  '영상 / 콘텐츠',
  '창업',
  '과학 / 기술'
];

const sortOptions = [
  { value: 'deadline', label: '마감 임박순' },
  { value: 'interest', label: '관심도순' },
  { value: 'latest', label: '최신 등록순' }
];

const ContestListPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get('category') || '전체';
  const initialSort = searchParams.get('sort_by') || 'deadline';

  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [sortBy, setSortBy] = useState(initialSort);
  const [searchQuery, setSearchQuery] = useState('');
  const [contests, setContests] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selectedContest, setSelectedContest] = useState(null);

  const fetchContests = async () => {
    try {
      setLoading(true);
      const res = await contestApi.getContests({
        category: selectedCategory === '전체' ? undefined : selectedCategory,
        search: searchQuery || undefined,
        sort_by: sortBy,
        page: page,
        page_size: 12
      });
      setContests(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to fetch contests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContests();
  }, [selectedCategory, sortBy, page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchContests();
  };

  const handleCategoryClick = (cat) => {
    setSelectedCategory(cat);
    setPage(1);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header & Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">공모전 탐색</h1>
          <p className="text-xs text-slate-500 mt-1">
            총 <span className="font-bold text-blue-600">{total}개</span>의 공모전이 접수 중입니다.
          </p>
        </div>

        {/* Search Bar & Sort Dropdown */}
        <div className="flex items-center gap-3">
          <form onSubmit={handleSearchSubmit} className="relative min-w-[240px] sm:min-w-[300px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="공모전 제목, 주최사 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white"
            />
          </form>

          <div className="relative shrink-0">
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
            >
              {sortOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => handleCategoryClick(cat)}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Contest Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(n => (
            <div key={n} className="h-64 rounded-2xl bg-slate-200/70 animate-pulse"></div>
          ))}
        </div>
      ) : contests.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contests.map((contest) => (
              <ContestCard
                key={contest.id}
                contest={contest}
                onSelect={setSelectedContest}
                onBookmarkChanged={fetchContests}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-2 pt-6">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              이전
            </button>
            <span className="text-xs font-bold text-slate-700 px-3">
              {page} / {Math.max(1, Math.ceil(total / 12))}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / 12)}
              className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              다음
            </button>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
          <AlertCircle className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">검색 조건에 맞는 공모전이 없습니다</h3>
          <p className="text-xs text-slate-500">다른 검색어나 카테고리 필터를 선택해보세요.</p>
        </div>
      )}

      {/* Modal */}
      <ContestDetailModal
        contest={selectedContest}
        isOpen={!!selectedContest}
        onClose={() => setSelectedContest(null)}
        onBookmarkChanged={fetchContests}
      />
    </div>
  );
};

export default ContestListPage;
