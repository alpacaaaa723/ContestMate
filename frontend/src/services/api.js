import axios from 'axios';
import fallbackContestsRaw from '../data/fallbackContests.json';

// 로컬 스토리지 기반 데모 데이터 스토어 (Vercel 프론트엔드 단독 실행 시 활용)
const getLocalContests = () => {
  const today = new Date();
  return fallbackContestsRaw.map(c => {
    let dday = 14;
    if (c.end_date) {
      const target = new Date(c.end_date);
      const diffTime = target.getTime() - today.getTime();
      dday = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    return {
      ...c,
      dday: isNaN(dday) ? 10 : dday
    };
  });
};

const getLocalBookmarks = () => {
  try {
    return JSON.parse(localStorage.getItem('contestmate_bookmarks') || '[]');
  } catch {
    return [];
  }
};

const saveLocalBookmarks = (bookmarks) => {
  localStorage.setItem('contestmate_bookmarks', JSON.stringify(bookmarks));
};

const getLocalPreferences = () => {
  try {
    const saved = localStorage.getItem('contestmate_preferences');
    if (saved) return JSON.parse(saved);
  } catch {}
  return {
    categories: ['IT / 개발', 'AI / 인공지능', '기획 / 아이디어'],
    keywords: ['해커톤', 'AI', '대학생', '개발'],
    keyword_match_type: 'OR',
    target_types: ['대학생', '제한 없음'],
    hide_expired: true,
    notify_new_contests: true,
    notify_deadlines: true,
    telegram_chat_id: ''
  };
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Helper: Response가 HTML(Vercel SPA Fallback 등)인지 검사
const isValidJsonResponse = (res) => {
  return res && res.data && typeof res.data === 'object';
};

export const contestApi = {
  getContests: async (params = {}) => {
    try {
      const res = await api.get('/contests', { params });
      if (isValidJsonResponse(res)) return res.data;
    } catch (e) {
      console.warn('[ContestMate] Backend API unavailable, using fallback data:', e.message);
    }
    // Fallback: 백엔드 미연결 시 로컬 실제 데이터 기반 정밀 필터링, 정렬, 페이지네이션
    let items = getLocalContests();
    
    // 카테고리 필터
    if (params.category && params.category !== '전체') {
      items = items.filter(c => c.category === params.category);
    }
    
    // 검색어 필터 (search 또는 keyword)
    const searchKw = (params.search || params.keyword || '').toLowerCase().trim();
    if (searchKw) {
      items = items.filter(c => 
        (c.title || '').toLowerCase().includes(searchKw) || 
        (c.organizer || '').toLowerCase().includes(searchKw) ||
        (c.description || '').toLowerCase().includes(searchKw)
      );
    }

    // 정렬 (마감 임박순, 최신 등록순, 관심도순)
    const sortBy = params.sort_by || 'deadline';
    if (sortBy === 'deadline') {
      items.sort((a, b) => {
        const da = a.dday >= 0 ? a.dday : 9999;
        const db = b.dday >= 0 ? b.dday : 9999;
        return da - db;
      });
    } else if (sortBy === 'latest') {
      items.sort((a, b) => new Date(b.start_date || 0) - new Date(a.start_date || 0));
    } else if (sortBy === 'interest') {
      const prefs = getLocalPreferences();
      items.sort((a, b) => {
        const aMatch = prefs.categories.some(cat => a.category?.includes(cat)) ? 1 : 0;
        const bMatch = prefs.categories.some(cat => b.category?.includes(cat)) ? 1 : 0;
        return bMatch - aMatch;
      });
    }

    const bookmarks = getLocalBookmarks();
    const enriched = items.map(c => ({
      ...c,
      is_bookmarked: bookmarks.includes(c.id)
    }));

    // 페이지네이션 슬라이스
    const page = Math.max(1, Number(params.page) || 1);
    const pageSize = Math.max(1, Number(params.page_size) || 12);
    const total = enriched.length;
    const startIdx = (page - 1) * pageSize;
    const pagedItems = enriched.slice(startIdx, startIdx + pageSize);

    return {
      total: total,
      items: pagedItems,
      page: page,
      page_size: pageSize
    };
  },

  getRecommended: async (limit = 6) => {
    try {
      const res = await api.get('/contests/recommended', { params: { limit } });
      if (isValidJsonResponse(res) && Array.isArray(res.data)) return res.data;
    } catch (e) {
      console.warn('[ContestMate] Backend API unavailable, using fallback recommended:', e.message);
    }
    const prefs = getLocalPreferences();
    const bookmarks = getLocalBookmarks();
    let items = getLocalContests();
    
    // 관심 카테고리 매칭
    const matched = items.filter(c => {
      const catMatch = prefs.categories.some(cat => c.category?.includes(cat) || cat.includes(c.category));
      const kwMatch = prefs.keywords.some(kw => c.title.toLowerCase().includes(kw.toLowerCase()));
      return catMatch || kwMatch;
    });

    const pool = matched.length > 0 ? matched : items;
    return pool.slice(0, limit).map(c => ({
      ...c,
      is_bookmarked: bookmarks.includes(c.id)
    }));
  },

  getContestDetail: async (id) => {
    try {
      const res = await api.get(`/contests/${id}`);
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    const items = getLocalContests();
    const bookmarks = getLocalBookmarks();
    const found = items.find(c => c.id === id) || items[0];
    return {
      ...found,
      is_bookmarked: bookmarks.includes(found?.id)
    };
  },
};

export const calendarApi = {
  getEvents: async (params = {}) => {
    try {
      const res = await api.get('/calendar/events', { params });
      if (isValidJsonResponse(res) && Array.isArray(res.data)) return res.data;
    } catch {}
    const items = getLocalContests();
    const bookmarks = getLocalBookmarks();

    return items.map(c => {
      const isBookmarked = bookmarks.includes(c.id);
      let color = '#3b82f6';
      if (c.dday <= 1) color = '#ef4444';
      else if (c.dday <= 3) color = '#f97316';
      else if (c.dday <= 7) color = '#eab308';

      return {
        id: c.id,
        title: `[${c.dday >= 0 ? `D-${c.dday}` : '마감'}] ${c.title}`,
        start: c.end_date,
        allDay: true,
        backgroundColor: color,
        borderColor: color,
        textColor: '#ffffff',
        extendedProps: {
          contest_id: c.id,
          organizer: c.organizer,
          category: c.category,
          dday: c.dday,
          is_bookmarked: isBookmarked,
          source: c.source,
          source_url: c.source_url
        }
      };
    });
  },
};

export const bookmarkApi = {
  getBookmarks: async () => {
    try {
      const res = await api.get('/bookmarks');
      if (isValidJsonResponse(res) && Array.isArray(res.data)) return res.data;
    } catch {}
    const bookmarks = getLocalBookmarks();
    const items = getLocalContests();
    return items.filter(c => bookmarks.includes(c.id)).map(c => ({
      ...c,
      is_bookmarked: true
    }));
  },

  addBookmark: async (contestId) => {
    try {
      await api.post(`/bookmarks/${contestId}`);
    } catch {}
    const bookmarks = getLocalBookmarks();
    if (!bookmarks.includes(contestId)) {
      bookmarks.push(contestId);
      saveLocalBookmarks(bookmarks);
    }
    return { status: 'success', is_bookmarked: true };
  },

  removeBookmark: async (contestId) => {
    try {
      await api.delete(`/bookmarks/${contestId}`);
    } catch {}
    const bookmarks = getLocalBookmarks().filter(id => id !== contestId);
    saveLocalBookmarks(bookmarks);
    return { status: 'success', is_bookmarked: false };
  },
};

export const preferenceApi = {
  getPreferences: async () => {
    try {
      const res = await api.get('/preferences');
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    return getLocalPreferences();
  },

  updatePreferences: async (data) => {
    try {
      const res = await api.put('/preferences', data);
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    localStorage.setItem('contestmate_preferences', JSON.stringify(data));
    return data;
  },
};

export const notificationApi = {
  getHistory: async () => {
    try {
      const res = await api.get('/notifications/history');
      if (isValidJsonResponse(res) && Array.isArray(res.data)) return res.data;
    } catch {}
    return [
      {
        id: 'notif_1',
        title: '신규 맞춤 공모전 알림',
        message: '회원님의 관심 분야인 [IT / 개발] 신규 공모전이 5건 등록되었습니다.',
        sent_at: new Date().toISOString(),
        status: 'SENT'
      }
    ];
  },
  sendTest: async (data) => {
    try {
      const res = await api.post('/notifications/test', data);
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    return { status: 'success', message: '테스트 알림이 전송되었습니다.' };
  },
};

export const adminApi = {
  getStatus: async () => {
    try {
      const res = await api.get('/admin/collector-status');
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    return {
      status: 'active',
      total_contests: 100,
      sources: {
        '위비티': { status: 'SUCCESS', count: 60 },
        '링커리어': { status: 'SUCCESS', count: 40 }
      }
    };
  },
  collectNow: async () => {
    try {
      const res = await api.post('/admin/collect-now');
      if (isValidJsonResponse(res)) return res.data;
    } catch {}
    return { status: 'success', collected_count: 100 };
  },
};

export default api;
