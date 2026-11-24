# 🏆 ContestMate - 개인 맞춤형 공모전 통합 알림 서비스

> 국내 주요 공모전 및 대외활동 포털(위비티, 링커리어, 캠퍼스픽, 올콘, 데브이벤트, 콘테스트코리아, 씽굿 등)의 실시간 데이터를 수집하여 500여 개 이상의 실제 공모전을 사용자 맞춤 추천, D-day 마감일 캘린더 관리, Telegram 마감 알림으로 제공하는 실시간 웹 & PWA 서비스입니다.

---

## 🛠 기술 스택

- **Frontend**: React 18 + Vite + Tailwind CSS + FullCalendar React + PWA (앱 설치 지원)
- **Backend**: Python 3.10+ + FastAPI + Pydantic v2 + APScheduler
- **Database & Auth**: Supabase PostgreSQL + Supabase Auth (RLS 적용)
- **Scraping**: BeautifulSoup4, httpx, REST/AJAX API, Markdown parser (위비티, 링커리어, 캠퍼스픽, 올콘, 데브이벤트, 콘테스트코리아, 씽굿 7대 독립 수집기)
- **Notification**: Telegram Bot API
- **Deployment**: Vercel (Frontend) + Render / Railway (Backend) + Docker

---

## 🧭 개발 단계 완료 현황 (1단계 ~ 12단계 전체 완료)

- [x] **1단계: 전체 시스템 아키텍처 및 프로젝트 폴더 구조 설계**
- [x] **2단계: 데이터베이스 설계 및 SQL 마이그레이션 (RLS, 인덱스, 트리거)**
- [x] **3단계: FastAPI 백엔드 및 인증 (Supabase JWT 연동 & 데모 모드 지원)**
- [x] **4단계: 공모전 데이터 수집 모듈 (Wevity, Thinkgood, Linkareer 독립 수집기)**
- [x] **5단계: 맞춤 공모전 매칭 (OR/AND 키워드, 카테고리, 참가대상, 상금 평가)**
- [x] **6단계: 북마크 기능 (저장, 해제, 사용자별 캘린더 연동)**
- [x] **7단계: 공모전 마감 캘린더 (FullCalendar React 연동, D-day 시각적 강조, 날짜별 팝오버)**
- [x] **8단계: Telegram 알림 (신규 공모전, 마감 D-7, D-3, D-1, 당일 알림, 발송 이력 로깅)**
- [x] **9단계: React 프론트엔드 구현 (Dashboard, ContestList, Calendar, Bookmarks, Preferences, Notifications)**
- [x] **10단계: 백엔드와 프론트엔드 연결 (Axios 인터셉터 & 프록시)**
- [x] **11단계: 전체 기능 테스트 (pytest 8개 테스트 100% 통과 & Vite 프로덕션 빌드 성공)**
- [x] **12단계: 배포 및 PWA 앱 패키징 (Vercel 설정, Dockerfile, PWA 앱 원클릭 설치 지원, DEPLOYMENT.md)**

---

## 📂 프로젝트 주요 구성

- [ARCHITECTURE.md](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/ARCHITECTURE.md): 시스템 아키텍처 및 데이터 흐름도
- [DEPLOYMENT.md](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/DEPLOYMENT.md): Vercel, Render/Railway, Supabase 배포 가이드
- [.env.example](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/.env.example): 환경변수 통합 템플릿
- [supabase/migrations/](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/supabase/migrations/): PostgreSQL DDL 및 RLS 정책
- [backend/](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/backend/): FastAPI 백엔드, 수집기, 매칭 엔진, 스케줄러
- [frontend/](file:///c:/Users/jinwoo/OneDrive/Desktop/contest/frontend/): React + Vite + Tailwind CSS + FullCalendar

---

## 🚀 빠른 시작 (Local Quickstart)

### 1. 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
- API Swagger 문서: http://localhost:8000/docs
- 테스트 실행: `pytest tests/test_backend.py -v`

### 2. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```
- 웹 접속: http://localhost:5173
