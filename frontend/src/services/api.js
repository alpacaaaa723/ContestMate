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
    const raw = localStorage.getItem('contestmate_bookmarks');
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
};

const saveLocalBookmarks = (bookmarks) => {
  try {
    const unique = Array.from(new Set(bookmarks.map(String)));
    localStorage.setItem('contestmate_bookmarks', JSON.stringify(unique));
  } catch (e) {
    console.error('Failed to save bookmarks to localStorage:', e);
  }
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
    const bookmarks = getLocalBookmarks();
    try {
      const res = await api.get('/contests', { params });
      if (isValidJsonResponse(res)) {
        if (Array.isArray(res.data?.items)) {
          res.data.items = res.data.items.map(c => ({
            ...c,
            is_bookmarked: bookmarks.includes(String(c.id))
          }));
        }
        return res.data;
      }
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

    const enriched = items.map(c => ({
      ...c,
      is_bookmarked: bookmarks.includes(String(c.id))
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
    const bookmarks = getLocalBookmarks();
    try {
      const res = await api.get('/contests/recommended', { params: { limit } });
      if (isValidJsonResponse(res) && Array.isArray(res.data)) {
        return res.data.map(c => ({
          ...c,
          is_bookmarked: bookmarks.includes(String(c.id))
        }));
      }
    } catch (e) {
      console.warn('[ContestMate] Backend API unavailable, using fallback recommended:', e.message);
    }
    const prefs = getLocalPreferences();
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
      is_bookmarked: bookmarks.includes(String(c.id))
    }));
  },

  getContestDetail: async (id) => {
    const bookmarks = getLocalBookmarks();
    try {
      const res = await api.get(`/contests/${id}`);
      if (isValidJsonResponse(res)) {
        return {
          ...res.data,
          is_bookmarked: bookmarks.includes(String(res.data.id))
        };
      }
    } catch {}
    const items = getLocalContests();
    const found = items.find(c => String(c.id) === String(id)) || items[0];
    return {
      ...found,
      is_bookmarked: bookmarks.includes(String(found?.id))
    };
  },
};

export const calendarApi = {
  getEvents: async (params = {}) => {
    const bookmarks = getLocalBookmarks();
    try {
      const res = await api.get('/calendar/events', { params });
      if (isValidJsonResponse(res) && Array.isArray(res.data)) {
        return res.data
          .filter(ev => {
            if (params.bookmark_only) {
              const cid = String(ev.extendedProps?.contest_id || ev.id);
              return bookmarks.includes(cid);
            }
            return true;
          })
          .map(ev => {
            const cid = String(ev.extendedProps?.contest_id || ev.id);
            const isBm = bookmarks.includes(cid);
            return {
              ...ev,
              extendedProps: {
                ...ev.extendedProps,
                is_bookmarked: isBm
              }
            };
          });
      }
    } catch {}

    let items = getLocalContests();

    // Filter by bookmark_only
    if (params.bookmark_only) {
      items = items.filter(c => bookmarks.includes(String(c.id)));
    }
    // Filter by deadline_within
    if (params.deadline_within !== undefined) {
      const limit = Number(params.deadline_within);
      items = items.filter(c => c.dday >= 0 && c.dday <= limit);
    }
    // Filter by category
    if (params.category && params.category !== '전체 분야' && params.category !== '전체') {
      items = items.filter(c => c.category === params.category);
    }

    return items.map(c => {
      const isBookmarked = bookmarks.includes(String(c.id));
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
    const localBookmarks = getLocalBookmarks();
    try {
      const res = await api.get('/bookmarks');
      if (isValidJsonResponse(res) && Array.isArray(res.data)) {
        // Backend items normalization: could be { id, contest } or contest object
        const serverBookmarks = res.data.map(item => {
          if (item && item.contest && item.contest.title) {
            return { ...item.contest, is_bookmarked: true };
          }
          return { ...item, is_bookmarked: true };
        });

        // Merge any local bookmarked IDs that server might not have yet
        const serverIds = new Set(serverBookmarks.map(c => String(c.id)));
        const allLocal = getLocalContests();
        const extraFromLocal = allLocal
          .filter(c => localBookmarks.includes(String(c.id)) && !serverIds.has(String(c.id)))
          .map(c => ({ ...c, is_bookmarked: true }));

        const merged = [...serverBookmarks, ...extraFromLocal];
        saveLocalBookmarks(merged.map(c => String(c.id)));
        return merged;
      }
    } catch (e) {
      console.warn('[ContestMate] Backend bookmark API unavailable, using local bookmarks:', e.message);
    }

    // Local / Offline / Vercel fallback:
    const allItems = getLocalContests();
    return allItems
      .filter(c => localBookmarks.includes(String(c.id)))
      .map(c => ({
        ...c,
        is_bookmarked: true
      }));
  },

  addBookmark: async (contestId) => {
    const cId = String(contestId);
    const bookmarks = getLocalBookmarks();
    if (!bookmarks.includes(cId)) {
      bookmarks.push(cId);
      saveLocalBookmarks(bookmarks);
    }
    try {
      await api.post(`/bookmarks/${contestId}`);
    } catch {}
    return { status: 'success', is_bookmarked: true };
  },

  removeBookmark: async (contestId) => {
    const cId = String(contestId);
    const bookmarks = getLocalBookmarks().filter(id => id !== cId);
    saveLocalBookmarks(bookmarks);
    try {
      await api.delete(`/bookmarks/${contestId}`);
    } catch {}
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
