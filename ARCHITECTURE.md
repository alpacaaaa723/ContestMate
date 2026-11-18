# ContestMate 시스템 아키텍처 및 폴더 구조 설계서

## 1. 시스템 아키텍처 개요

ContestMate는 국내 공모전 및 대외활동 정보(위비티, 씽굿, 링커리어 등)를 수집하여 사용자 맞춤 추천, D-day 기반 캘린더 관리, Telegram 마감 알림을 제공하는 모듈형 풀스택 웹 서비스입니다.

```
                           +----------------------------------------+
                           |           User Web Browser             |
                           |   (React + Vite + Tailwind CSS)        |
                           +-------------------+--------------------+
                                               |
                          REST API / JSON      | Auth (Supabase Client)
                                               v
+-------------------+      +----------------------------------------+      +--------------------+
|                   |      |           FastAPI Backend              |      |                    |
| Telegram Bot API  |<-----+ - Auth Verification (JWT)              +----->| Supabase PostgreSQL|
| (Deadline/New)    |      | - Contest Matcher Engine               |      | & Supabase Auth    |
+-------------------+      | - FullCalendar Event Formatter         |      +---------^----------+
                           | - APScheduler (Cron Jobs)              |                |
                           +-------------------+--------------------+                |
                                               |                                     |
                                               v (Runs scheduled / on-demand)        |
                           +----------------------------------------+                |
                           |        Data Collector Engine           |                |
                           |  - Wevity Collector (BS4/HTTP)         +----------------+
                           |  - Thinkgood Collector (BS4/HTTP)      |  (Saves new contests &
                           |  - Linkareer Collector (API/Playwright)|   logs to DB)
                           +----------------------------------------+
```

---

## 2. 계층별 기술 스택 및 역할

| 계층 | 기술 스택 | 주요 역할 |
|---|---|---|
| **Frontend** | React 18, Vite, JavaScript, Tailwind CSS | - 반응형 UI (Dashboard, Contest List, Calendar, Bookmarks, Preferences)<br>- FullCalendar React 연동<br>- Supabase Auth 클라이언트 및 상태 관리 |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2 | - RESTful API 제공 (`/api/contests`, `/api/calendar/events` 등)<br>- 사용자 맞춤 추천(OR/AND 키워드 및 카테고리 매칭)<br>- Supabase JWT 토큰 검증 및 RLS 호환 권한 제어 |
| **Database** | Supabase PostgreSQL, Supabase Auth | - RLS(Row Level Security) 적용된 사용자 데이터 보안<br>- 인덱싱 기반의 날짜, 카테고리 고속 쿼리<br>- 마이그레이션 버전 관리 (`supabase/migrations`) |
| **Scraper** | BeautifulSoup4, httpx/requests, Playwright | - 사이트별 독립 Collector 추상 클래스 상속 구조<br>- 데이터 정규화(날짜, 분야, 상금 등)<br>- robots.txt 확인 및 수집 실패 시 collector_logs 기록 |
| **Scheduler** | APScheduler (AsyncIOScheduler) | - 주기적 공모전 수집 트리거 (예: 6시간 주기)<br>- 일일/주간 마감 임박 및 신규 공모전 Telegram 알림 발송 |
| **Notification** | Telegram Bot API (httpx / python-telegram-bot) | - 마감 D-7, D-3, D-1, 당일 알림 및 신규 공모전 알림 발송<br>- 알림 발송 이력(`notification_logs`) 기록 및 중복 방지 |

---

## 3. 상세 디렉토리 구조

```
contest/
├── .env.example                     # 전체 환경변수 템플릿
├── .gitignore                       # Git 무시 파일 목록
├── README.md                        # 프로젝트 설명 및 단계별 실행 안내
├── ARCHITECTURE.md                  # 본 시스템 아키텍처 문서
│
├── backend/                         # FastAPI 백엔드
│   ├── requirements.txt             # Python 패키지 의존성
│   ├── .env.example                 # 백엔드 전용 환경변수 템플릿
│   ├── main.py                      # FastAPI 엔트리포인트 & 라이프사이클 (APScheduler 초기화)
│   ├── app/
│   │   ├── api/                     # API 라우팅
│   │   │   └── v1/
│   │   │       ├── api.py           # v1 라우터 통합
│   │   │       └── endpoints/
│   │   │           ├── auth.py          # 사용자 프로필 / 인증 보조
│   │   │           ├── contests.py      # 공모전 목록, 상세, 추천
│   │   │           ├── bookmarks.py     # 북마크 CRUD
│   │   │           ├── calendar.py      # FullCalendar 규격 이벤트 API
│   │   │           ├── preferences.py   # 관심 분야 / 키워드 설정
│   │   │           ├── notifications.py # 알림 이력 및 테스트
│   │   │           └── admin.py         # 수집기 상태 및 로그 조회
│   │   ├── core/                    # 핵심 설정 및 유틸
│   │   │   ├── config.py            # Pydantic BaseSettings 설정
│   │   │   ├── security.py          # JWT 검증 및 사용자 의존성 주입 (get_current_user)
│   │   │   ├── database.py          # Supabase Client / DB 커넥션 관리
│   │   │   └── scheduler.py         # APScheduler 백그라운드 작업 등록
│   │   ├── collectors/              # 공모전 데이터 수집 모듈 (독립 구조)
│   │   │   ├── base.py              # BaseCollector 추상 클래스
│   │   │   ├── wevity.py            # 위비티 Collector
│   │   │   ├── thinkgood.py         # 씽굿 Collector
│   │   │   ├── linkareer.py         # 링커리어 Collector
│   │   │   └── runner.py            # 전체 Collector 통합 실행기
│   │   ├── models/                  # 데이터베이스 매핑 모델 (SQLAlchemy or Dict Typings)
│   │   │   └── contest.py
│   │   ├── schemas/                 # Pydantic 입출력 DTO 검증 스키마
│   │   │   ├── contest.py
│   │   │   ├── preference.py
│   │   │   ├── bookmark.py
│   │   │   ├── calendar.py
│   │   │   └── notification.py
│   │   └── services/                # 비즈니스 로직
│   │       ├── contest_service.py   # 공모전 쿼리 및 필터링
│   │       ├── matcher_service.py   # 맞춤 추천 알고리즘 (OR/AND)
│   │       ├── calendar_service.py  # 캘린더 이벤트 빌더 (D-day 계산)
│   │       └── telegram_service.py  # 텔레그램 메시지 템플릿 및 발송
│   └── tests/                       # 단위 및 통합 테스트
│       ├── test_collectors.py
│       ├── test_matcher.py
│       └── test_calendar.py
│
├── frontend/                        # React + Vite 프론트엔드
│   ├── package.json                 # Node.js 의존성
│   ├── vite.config.js               # Vite 설정 (Proxy 등)
│   ├── tailwind.config.js           # Tailwind CSS 테마 설정
│   ├── postcss.config.js
│   ├── index.html                   # HTML 진입점
│   ├── src/
│   │   ├── main.jsx                 # React root render
│   │   ├── App.jsx                  # React Router 라우팅 및 전역 레이아웃
│   │   ├── index.css                # Tailwind directives & 전역 스타일
│   │   ├── assets/                  # 정적 리소스 (로고, 아이콘 등)
│   │   ├── components/
│   │   │   ├── common/              # 공통 컴포넌트 (Sidebar, Navbar, Modal, Badge, DDayTag)
│   │   │   ├── dashboard/           # 대시보드 위젯 (통계 카드, 마감 임박 목록)
│   │   │   ├── contest/             # 공모전 카드, 필터 바, 상세 모달/페이지
│   │   │   ├── calendar/            # FullCalendar 래퍼, 날짜 클릭 팝오버, 범례
│   │   │   ├── preferences/         # 관심 설정 폼 (태그 인풋, AND/OR 선택)
│   │   │   └── bookmarks/           # 북마크 리스트 컴포넌트
│   │   ├── context/                 # AuthContext (Supabase 세션 관리)
│   │   ├── hooks/                   # useContests, useBookmarks, useCalendar 커스텀 훅
│   │   ├── pages/                   # 라우팅 페이지
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ContestListPage.jsx
│   │   │   ├── ContestDetailPage.jsx
│   │   │   ├── CalendarPage.jsx
│   │   │   ├── PreferencesPage.jsx
│   │   │   ├── BookmarksPage.jsx
│   │   │   ├── NotificationsPage.jsx
│   │   │   └── LoginPage.jsx
│   │   ├── services/                # Axios / Fetch API 모듈
│   │   │   ├── api.js               # 인터셉터 설정된 기본 API 클라이언트
│   │   │   ├── contestApi.js
│   │   │   ├── bookmarkApi.js
│   │   │   ├── calendarApi.js
│   │   │   └── preferenceApi.js
│   │   └── utils/                   # 날짜 포맷팅, D-day 계산기, 텍스트 하이라이터
│   │       ├── dateUtils.js
│   │       └── ddayCalculator.js
│
└── supabase/                        # 데이터베이스 마이그레이션 및 RLS
    └── migrations/
        ├── 20261117_000001_initial_schema.sql      # 기본 6개 테이블 및 인덱스
        ├── 20261117_000002_rls_policies.sql        # RLS 접근 제어 정책
        └── 20261117_000003_triggers_functions.sql   # updated_at 트리거 등
```

---

## 4. 데이터 흐름 및 핵심 시퀀스

### 4-1. 공모전 데이터 수집 및 가공
1. `scheduler.py` 또는 관리자 API가 `runner.py` 실행
2. 각 사이트별 Collector(`wevity.py`, `thinkgood.py`, `linkareer.py`)가 최신 목록 크롤링
3. 수집 데이터 검증 및 일자/카테고리 정규화
4. `contests` 테이블에 UPSERT (동일 원본 URL 또는 고유 키 기준 중복 방지)
5. `collector_logs`에 실행 결과(수집 건수, 소요시간, 상태, 에러 메시지) 기록

### 4-2. 사용자 맞춤 추천 및 캘린더 생성
1. 클라이언트가 JWT 토큰과 함께 `GET /api/contests/recommended` 또는 `GET /api/calendar/events` 요청
2. `security.py`가 토큰을 검증하고 `user_id` 식별
3. 사용자의 `user_preferences` 및 `bookmarks` 조회
4. 매칭 엔진이 카테고리 일치도 및 키워드(OR/AND 조건) 일치도를 연산
5. 캘린더 요청의 경우, 마감일(`end_date`)을 `start`로 두고 D-day별 시각적 색상/라벨을 부여하여 FullCalendar 표준 이벤트 DTO로 변환 반환

### 4-3. 마감 임박 및 신규 공모전 텔레그램 알림
1. APScheduler가 매일 지정 시간(예: 오전 9시)에 알림 잡 실행
2. 활성화된 `user_preferences` 중 `telegram_chat_id`가 등록된 사용자 탐색
3. 사용자가 북마크했거나 맞춤 추천에 해당하는 공모전 중 D-7, D-3, D-1, D-day에 해당하는 목록 필터링
4. `notification_logs`를 조회하여 당일 이미 발송된 알림인지 중복 여부 확인
5. Telegram Bot API로 메시지 포맷팅 후 발송 및 성공 여부 로깅

---

## 5. 다음 단계 계획
- **2단계: 데이터베이스 설계 및 SQL 마이그레이션**
  - `users`, `user_preferences`, `contests`, `bookmarks`, `notification_logs`, `collector_logs` 테이블 정의
  - 인덱스, 외래키 제약조건, RLS 정책 수립
  - `supabase/migrations/`에 실제 적용 가능한 SQL 작성
