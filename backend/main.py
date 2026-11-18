from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.collectors.runner import collector_runner

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 초기 데이터 적재 및 스케줄러 시작
    print("[ContestMate] Starting backend application...")
    try:
        # 최초 기본 데이터 동기화
        await collector_runner.run_all()
    except Exception as e:
        print(f"[ContestMate] Initial data collection notice: {e}")
    
    start_scheduler()
    yield
    # 앱 종료 시 스케줄러 정리 및 클라이언트 종료
    print("[ContestMate] Shutting down backend application...")
    shutdown_scheduler()
    await collector_runner.close_all()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ContestMate - 개인 맞춤형 공모전 통합 알림 서비스 백엔드 API",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": "ContestMate API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
