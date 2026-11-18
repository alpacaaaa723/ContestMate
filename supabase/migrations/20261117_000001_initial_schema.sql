-- ============================================================
-- 1. EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 2. USERS TABLE (Supabase auth.users 연동 및 프로필)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- ============================================================
-- 3. USER PREFERENCES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    categories TEXT[] DEFAULT '{}'::TEXT[],
    keywords TEXT[] DEFAULT '{}'::TEXT[],
    keyword_match_type TEXT DEFAULT 'OR' CHECK (keyword_match_type IN ('OR', 'AND')),
    target_types TEXT[] DEFAULT '{}'::TEXT[],
    hide_expired BOOLEAN DEFAULT FALSE,
    notify_new_contests BOOLEAN DEFAULT TRUE,
    notify_deadlines BOOLEAN DEFAULT TRUE,
    telegram_chat_id TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    CONSTRAINT uq_user_preferences_user_id UNIQUE (user_id)
);

-- ============================================================
-- 4. CONTESTS TABLE (수집된 공모전 데이터)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.contests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    organizer TEXT NOT NULL,
    category TEXT NOT NULL,
    target_type TEXT DEFAULT '제한없음',
    description TEXT,
    prize TEXT,
    start_date DATE,
    end_date DATE NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    thumbnail_url TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    last_crawled_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 인덱스 설정 (캘린더 및 필터링 검색 최적화)
CREATE INDEX IF NOT EXISTS idx_contests_end_date ON public.contests(end_date);
CREATE INDEX IF NOT EXISTS idx_contests_category ON public.contests(category);
CREATE INDEX IF NOT EXISTS idx_contests_source ON public.contests(source);
CREATE INDEX IF NOT EXISTS idx_contests_target_type ON public.contests(target_type);
CREATE INDEX IF NOT EXISTS idx_contests_created_at ON public.contests(created_at DESC);

-- ============================================================
-- 5. BOOKMARKS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    contest_id UUID NOT NULL REFERENCES public.contests(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    CONSTRAINT uq_bookmarks_user_contest UNIQUE (user_id, contest_id)
);

CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON public.bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_contest_id ON public.bookmarks(contest_id);

-- ============================================================
-- 6. NOTIFICATION LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.notification_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    contest_id UUID REFERENCES public.contests(id) ON DELETE SET NULL,
    notification_type TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_notification_logs_user_sent ON public.notification_logs(user_id, sent_at DESC);

-- ============================================================
-- 7. COLLECTOR LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.collector_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'PARTIAL', 'FAILED')),
    collected_count INT DEFAULT 0 NOT NULL,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_collector_logs_source_started ON public.collector_logs(source, started_at DESC);
