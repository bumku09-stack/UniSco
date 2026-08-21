import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.match import router as match_router
from app.api.scholarships import router as scholarships_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.ghost_accounts import run_ghost_account_cleanup_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버가 켜져 있는 동안 계속 도는 백그라운드 청소부(core/ghost_accounts.py 참고) —
    # 종료 시 태스크를 취소해서 재시작할 때 중복으로 안 쌓이게 함.
    cleanup_task = asyncio.create_task(run_ghost_account_cleanup_loop())
    yield
    cleanup_task.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scholarships_router)
app.include_router(match_router)
app.include_router(auth_router)
app.include_router(users_router)
