import React, { useState, useEffect, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { 
  Calendar as CalendarIcon, 
  Filter, 
  Bookmark, 
  Sparkles, 
  Clock, 
  ListFilter,
  X,
  ExternalLink
} from 'lucide-react';
import { calendarApi, contestApi } from '../services/api';
import ContestDetailModal from '../components/common/ContestDetailModal';
import DDayBadge from '../components/common/DDayBadge';

const categories = [
  '전체 분야',
  'IT / 개발',
  'AI / 인공지능',
  '기획 / 아이디어',
  '디자인',
  '마케팅',
  '영상 / 콘텐츠',
  '창업'
];

const CalendarPage = () => {
  const calendarRef = useRef(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState('all'); // all | bookmark | urgent | recommended
  const [selectedCategory, setSelectedCategory] = useState('전체 분야');

  // Selected Date Modal for clicking a specific calendar date cell
  const [dateModalOpen, setDateModalOpen] = useState(false);
  const [clickedDate, setClickedDate] = useState('');
  const [dateEvents, setDateEvents] = useState([]);

  // Selected Contest Modal
  const [selectedContest, setSelectedContest] = useState(null);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterType === 'bookmark') params.bookmark_only = true;
      if (filterType === 'urgent') params.deadline_within = 3;
      if (selectedCategory !== '전체 분야') params.category = selectedCategory;

      const data = await calendarApi.getEvents(params);
      setEvents(data);
    } catch (err) {
      console.error('Failed to fetch calendar events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [filterType, selectedCategory]);

  // Handle Event Click
  const handleEventClick = async (info) => {
    info.jsEvent.preventDefault();
    const contestId = info.event.id;
    try {
      const detail = await contestApi.getContestDetail(contestId);
      setSelectedContest(detail);
    } catch (err) {
      // Fallback: extendedProps 기반으로 구성
      const props = info.event.extendedProps || {};
      setSelectedContest({
        id: contestId,
        title: info.event.title.replace(/^\[.*?\]\s*/, ''),
        organizer: props.organizer,
        category: props.category,
        target_type: props.target_type,
        dday: props.dday,
        prize: props.prize,
        description: props.description,
        source: props.source,
        source_url: props.sourceUrl,
        end_date: info.event.startStr,
        is_bookmarked: props.isBookmarked
      });
    }
  };

  // Handle Date Cell Click
  const handleDateClick = (arg) => {
    const clickedDateStr = arg.dateStr;
    const matching = events.filter(e => e.start === clickedDateStr);
    setClickedDate(clickedDateStr);
    setDateEvents(matching);
    setDateModalOpen(true);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Filter Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <CalendarIcon className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-black text-slate-900 tracking-tight">공모전 마감 캘린더</h1>
              <p className="text-xs text-slate-500">마감일(D-day) 기준으로 공모전 일정을 한눈에 관리하세요.</p>
            </div>
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center gap-2">
            <ListFilter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-bold text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pt-2 border-t border-slate-100 scrollbar-none">
          <button
            onClick={() => setFilterType('all')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              filterType === 'all'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>전체 공모전</span>
          </button>

          <button
            onClick={() => setFilterType('bookmark')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              filterType === 'bookmark'
                ? 'bg-amber-500 text-white shadow-md shadow-amber-500/20'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>북마크한 공모전</span>
          </button>

          <button
            onClick={() => setFilterType('urgent')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              filterType === 'urgent'
                ? 'bg-rose-500 text-white shadow-md shadow-rose-500/20'
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>마감 임박 (D-3 이내)</span>
          </button>
        </div>

        {/* Urgency Legend */}
        <div className="flex flex-wrap items-center gap-3 pt-3 text-[11px] text-slate-500 font-medium">
          <span className="font-bold text-slate-700">D-day 구분:</span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse"></span> 오늘 마감 (D-Day)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> D-1 ~ D-2 (강조)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> D-3 ~ D-6 (주의)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> D-7 이상 (일반)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span> 마감 완료
          </span>
        </div>
      </div>

      {/* Calendar Card */}
      <div className="bg-white rounded-3xl p-4 sm:p-6 border border-slate-200/80 shadow-sm relative">
        {loading && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-20 flex items-center justify-center rounded-3xl">
            <div className="flex items-center gap-2 text-sm font-bold text-blue-600">
              <span className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></span>
              캘린더 일정 갱신 중...
            </div>
          </div>
        )}

        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          headerToolbar={{
            left: 'prev,today,next',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
          }}
          buttonText={{
            today: '오늘',
            month: '월간',
            week: '주간',
            day: '일간'
          }}
          events={events}
          eventClick={handleEventClick}
          dateClick={handleDateClick}
          locale="ko"
          dayMaxEvents={3}
          height="auto"
          displayEventTime={false}
        />
      </div>

      {/* Clicked Date Details Modal */}
      {dateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
          <div 
            className="bg-white rounded-3xl max-w-lg w-full max-h-[80vh] overflow-y-auto shadow-2xl border border-slate-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white z-10">
              <div>
                <h3 className="font-extrabold text-lg text-slate-900">
                  📅 {clickedDate} 마감 공모전
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  총 <span className="font-bold text-blue-600">{dateEvents.length}개</span>의 공모전이 마감됩니다.
                </p>
              </div>
              <button 
                onClick={() => setDateModalOpen(false)}
                className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-3">
              {dateEvents.length > 0 ? (
                dateEvents.map(evt => {
                  const props = evt.extendedProps || {};
                  return (
                    <div 
                      key={evt.id}
                      onClick={() => {
                        setDateModalOpen(false);
                        handleEventClick({ jsEvent: { preventDefault: () => {} }, event: evt });
                      }}
                      className="p-4 rounded-2xl border border-slate-200/80 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer bg-slate-50/50"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                          {props.category}
                        </span>
                        <DDayBadge dday={props.dday} />
                      </div>
                      <h4 className="font-bold text-slate-900 text-sm mb-1 leading-snug">
                        {evt.title.replace(/^\[.*?\]\s*/, '')}
                      </h4>
                      <p className="text-xs text-slate-500 truncate">
                        주최: {props.organizer}
                      </p>
                    </div>
                  );
                })
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">
                  이 날짜에 마감되는 공모전이 없습니다.
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-100 bg-slate-50/50 text-right">
              <button
                onClick={() => setDateModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-200 text-slate-700 font-bold text-xs hover:bg-slate-300 transition"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Contest Detail Modal */}
      <ContestDetailModal
        contest={selectedContest}
        isOpen={!!selectedContest}
        onClose={() => setSelectedContest(null)}
        onBookmarkChanged={fetchEvents}
      />
    </div>
  );
};

export default CalendarPage;
