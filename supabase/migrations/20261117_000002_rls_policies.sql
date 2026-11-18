-- ============================================================
-- 1. ROW LEVEL SECURITY (RLS) 활성화
-- ============================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collector_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 2. USERS POLICIES
-- ============================================================
CREATE POLICY "Users can view their own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- ============================================================
-- 3. USER PREFERENCES POLICIES
-- ============================================================
CREATE POLICY "Users can view their own preferences"
    ON public.user_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences"
    ON public.user_preferences FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences"
    ON public.user_preferences FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================================
-- 4. CONTESTS POLICIES (누구나 조회 가능, 쓰기는 서비스 롤)
-- ============================================================
CREATE POLICY "Anyone can view contests"
    ON public.contests FOR SELECT
    TO authenticated, anon
    USING (true);

-- ============================================================
-- 5. BOOKMARKS POLICIES
-- ============================================================
CREATE POLICY "Users can view their own bookmarks"
    ON public.bookmarks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own bookmarks"
    ON public.bookmarks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own bookmarks"
    ON public.bookmarks FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- 6. NOTIFICATION LOGS POLICIES
-- ============================================================
CREATE POLICY "Users can view their own notification logs"
    ON public.notification_logs FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================
-- 7. COLLECTOR LOGS POLICIES (인증된 사용자는 상태 확인 가능)
-- ============================================================
CREATE POLICY "Authenticated users can view collector logs"
    ON public.collector_logs FOR SELECT
    TO authenticated
    USING (true);

-- ============================================================
-- 8. TRIGGERS: auto updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_preferences_updated_at ON public.user_preferences;
CREATE TRIGGER trg_user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_contests_updated_at ON public.contests;
CREATE TRIGGER trg_contests_updated_at
    BEFORE UPDATE ON public.contests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 신규 유저 생성 시 자동으로 public.users 및 기본 preferences 생성 트리거
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, created_at)
    VALUES (NEW.id, NEW.email, NEW.created_at)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO public.user_preferences (user_id, categories, keywords, keyword_match_type)
    VALUES (NEW.id, ARRAY['IT / 개발', 'AI / 인공지능'], ARRAY['해커톤', 'AI', '개발'], 'OR')
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
