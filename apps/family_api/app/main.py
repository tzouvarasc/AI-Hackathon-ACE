from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from apps.family_api.app.config import settings
from apps.family_api.app.db import get_session, init_db
from apps.family_api.app.repository import FamilyRepository
from apps.family_api.app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from shared.contracts.schemas import (
    DashboardIngestRequest,
    DashboardInsights,
    DashboardSnapshot,
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserRole,
    UserView,
)

app = FastAPI(title="Thalpo Family API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    async for session in get_session():
        await FamilyRepository.ensure_admin_user(
            session=session,
            username=settings.bootstrap_admin_username,
            password_hash=hash_password(settings.bootstrap_admin_password),
            display_name=settings.bootstrap_admin_display_name,
        )
        break


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "family_api"}


@app.post("/v1/auth/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await FamilyRepository.get_user_by_username(session, request.username)
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    role = UserRole(user.role)
    token, expires_in = create_access_token(subject=user.username, role=role)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        role=role,
        user_id=user.user_id,
    )


@app.get("/v1/auth/me", response_model=UserView)
async def me(current_user=Depends(get_current_user)) -> UserView:
    return FamilyRepository.to_user_view(current_user)


@app.post("/v1/auth/users", response_model=UserView)
async def create_user(
    request: UserCreateRequest,
    session: AsyncSession = Depends(get_session),
    _=Depends(require_roles(UserRole.admin)),
) -> UserView:
    existing = await FamilyRepository.get_user_by_username(session, request.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = await FamilyRepository.create_user(
        session=session,
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
        display_name=request.display_name or request.username,
    )
    return FamilyRepository.to_user_view(user)


@app.post("/v1/dashboard/{user_id}/ingest", response_model=DashboardSnapshot)
async def ingest(
    user_id: str,
    payload: DashboardIngestRequest,
    x_internal_token: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> DashboardSnapshot:
    if x_internal_token != settings.internal_service_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")

    if payload.user_id != user_id:
        payload = payload.model_copy(update={"user_id": user_id})

    return await FamilyRepository.ingest_event(session, payload)


@app.get("/v1/dashboard/{user_id}", response_model=DashboardSnapshot)
async def get_dashboard(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    _=Depends(require_roles(UserRole.admin, UserRole.caregiver, UserRole.clinician)),
) -> DashboardSnapshot:
    return await FamilyRepository.get_snapshot(session, user_id)


@app.get("/v1/dashboard/{user_id}/history", response_model=list[DashboardIngestRequest])
async def get_history(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    _=Depends(require_roles(UserRole.admin, UserRole.caregiver, UserRole.clinician)),
) -> list[DashboardIngestRequest]:
    return await FamilyRepository.get_history(session, user_id=user_id, limit=limit)


@app.get("/v1/dashboard/{user_id}/insights", response_model=DashboardInsights)
async def get_insights(
    user_id: str,
    days: int = Query(default=30, ge=1, le=180),
    session: AsyncSession = Depends(get_session),
    _=Depends(require_roles(UserRole.admin, UserRole.caregiver, UserRole.clinician)),
) -> DashboardInsights:
    return await FamilyRepository.get_insights(session, user_id=user_id, days=days)
