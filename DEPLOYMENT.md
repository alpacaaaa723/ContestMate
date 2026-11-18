# ContestMate 배포 및 운영 가이드 (Deployment Guide)

본 문서는 ContestMate의 프론트엔드(Vercel), 백엔드(Render / Railway), 데이터베이스(Supabase) 배포 방법과 환경변수 설정 가이드를 다룹니다.

---

## 1. Supabase 데이터베이스 설정

1. [Supabase](https://supabase.com)에 로그인 후 신규 프로젝트를 생성합니다.
2. 좌측 메뉴의 **SQL Editor**로 이동합니다.
3. 다음 마이그레이션 파일들을 순서대로 복사하여 실행합니다:
   - [supabase/migrations/20261117_000001_initial_schema.sql](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/supabase/migrations/20261117_000001_initial_schema.sql)
   - [supabase/migrations/20261117_000002_rls_policies.sql](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/supabase/migrations/20261117_000002_rls_policies.sql)
4. **Project Settings > API**에서 다음 키를 복사합니다:
   - `Project URL`
   - `anon public key`
   - `service_role secret key`
   - `JWT Secret`

---

## 2. Telegram Bot API 설정

1. 텔레그램 앱에서 `@BotFather`를 검색합니다.
2. `/newbot` 명령어를 입력하고 봇 이름과 사용자명을 입력합니다.
3. 발급된 **HTTP API 토큰**(`TELEGRAM_BOT_TOKEN`)을 복사합니다.
4. 사용자는 봇을 시작(`/start`)한 후 자신의 Chat ID(`@userinfobot` 등 활용)를 ContestMate [맞춤 설정] 페이지에 입력하면 알림 연동이 완료됩니다.

---

## 3. 백엔드 배포 (Render 또는 Railway)

### Option A: Render
1. [Render Dashboard](https://dashboard.render.com/)에서 **New > Web Service** 선택.
2. GitHub 저장소 연결 후 `Root Directory`를 `backend`로 지정.
3. 빌드 및 시작 명령어:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** 설정:
   ```env
   ENVIRONMENT=production
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   BACKEND_CORS_ORIGINS=["https://contestmate.vercel.app"]
   ```

### Option B: Railway
1. [Railway](https://railway.app/) 대시보드에서 **Deploy from GitHub repo** 선택.
2. Root Directory를 `backend`로 설정.
3. `backend/Dockerfile`이 자동으로 감지되어 컨테이너로 빌드 및 실행됩니다.

---

## 4. 프론트엔드 배포 (Vercel)

1. [Vercel Dashboard](https://vercel.com/)에서 **Add New > Project** 선택.
2. 저장소 선택 후 **Root Directory**를 `frontend`로 지정.
3. Framework Preset: **Vite** 선택.
4. **Environment Variables** 설정:
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   VITE_API_BASE_URL=https://your-backend.onrender.com/api
   ```
5. **Deploy** 버튼 클릭.

---

## 5. 로컬 개발 환경 실행 방법

### 백엔드 실행 (Terminal 1)
```bash
cd backend
# 가상환경 활성화 후
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

### 프론트엔드 실행 (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
- 웹 접속: http://localhost:5173
