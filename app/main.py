import re
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import get_session, init_db
from .models import (
    Case,
    CaseCreate,
    CaseRead,
    CaseUpdate,
    DefenseDossier,
    DefenseDossierDocument,
    DefenseDossierParty,
    Document,
    DocumentCreate,
    DocumentRead,
    Hearing,
    HearingCreate,
    HearingRead,
    Party,
    PartyCreate,
    PartyRead,
    Task,
    TaskCreate,
    TaskRead,
)
from .settings import settings

MAX_UPLOAD_BYTES = settings.max_upload_mb * 1024 * 1024


def _sanitize_filename(name: str) -> str:
    """Strip path components and neutralize unsafe characters."""
    name = (name or "").replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[^\w\-. ]", "_", name)
    return name[:255] or "upload"


def require_api_key(x_api_key: str = Header(default="")) -> None:
    """Enforce API key auth when API_KEYS is set; no-op in dev mode."""
    if not settings.api_keys:
        return
    allowed = {k.strip() for k in settings.api_keys.split(",") if k.strip()}
    if x_api_key not in allowed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if not settings.api_keys:
        print(
            "WARNING: API_KEYS is not set — the API is unauthenticated. "
            "Do not expose it publicly.",
            flush=True,
        )
    yield


router = APIRouter(dependencies=[Depends(require_api_key)])

app = FastAPI(
    title="Legal Case Management API",
    version="0.1.0",
    lifespan=lifespan,
)


@router.post("/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    *, payload: CaseCreate, session: AsyncSession = Depends(get_session)
) -> CaseRead:
    case = Case.model_validate(payload)
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@router.get("/cases", response_model=List[CaseRead])
async def list_cases(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[CaseRead]:
    result = await session.exec(select(Case).offset(skip).limit(limit))
    return result.all()


@router.get("/cases/{case_id}", response_model=CaseRead)
async def get_case(
    case_id: int, session: AsyncSession = Depends(get_session)
) -> CaseRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.patch("/cases/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: int, *, payload: CaseUpdate, session: AsyncSession = Depends(get_session)
) -> CaseRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)
    case.updated_at = datetime.utcnow()

    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    await session.delete(case)
    await session.commit()


@router.post(
    "/cases/{case_id}/parties", response_model=PartyRead, status_code=status.HTTP_201_CREATED
)
async def add_party(
    case_id: int, *, payload: PartyCreate, session: AsyncSession = Depends(get_session)
) -> PartyRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    party = Party.model_validate(payload)
    session.add(party)
    await session.commit()
    await session.refresh(party)
    return party


@router.get("/cases/{case_id}/parties", response_model=List[PartyRead])
async def list_parties(
    case_id: int,
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[PartyRead]:
    result = await session.exec(
        select(Party).where(Party.case_id == case_id).offset(skip).limit(limit)
    )
    return result.all()


@router.post(
    "/cases/{case_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    case_id: int,
    payload: DocumentCreate,
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    document = Document.model_validate(payload)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.get("/cases/{case_id}/documents", response_model=List[DocumentRead])
async def list_documents(
    case_id: int,
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[DocumentRead]:
    result = await session.exec(
        select(Document).where(Document.case_id == case_id).offset(skip).limit(limit)
    )
    return result.all()


@router.post(
    "/cases/{case_id}/hearings",
    response_model=HearingRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_hearing(
    case_id: int, *, payload: HearingCreate, session: AsyncSession = Depends(get_session)
) -> HearingRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    hearing = Hearing.model_validate(payload)
    session.add(hearing)
    await session.commit()
    await session.refresh(hearing)
    return hearing


@router.get("/cases/{case_id}/hearings", response_model=List[HearingRead])
async def list_hearings(
    case_id: int,
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[HearingRead]:
    result = await session.exec(
        select(Hearing).where(Hearing.case_id == case_id).offset(skip).limit(limit)
    )
    return result.all()


@router.post(
    "/cases/{case_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED
)
async def add_task(
    case_id: int, *, payload: TaskCreate, session: AsyncSession = Depends(get_session)
) -> TaskRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    task = Task.model_validate(payload)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("/cases/{case_id}/tasks", response_model=List[TaskRead])
async def list_tasks(
    case_id: int,
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[TaskRead]:
    result = await session.exec(
        select(Task).where(Task.case_id == case_id).offset(skip).limit(limit)
    )
    return result.all()


@router.post(
    "/cases/{case_id}/documents/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_file(
    case_id: int,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    filename = _sanitize_filename(file.filename or "")
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {settings.max_upload_mb} MB)",
        )

    dest_dir = Path(settings.upload_dir) / str(case_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    if dest.exists():
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dest = dest_dir / f"{dest.stem}-{stamp}{dest.suffix}"
    dest.write_bytes(content)

    document = Document(
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
        description=f"Uploaded via multipart ({len(content)} bytes)",
        case_id=case_id,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.get("/cases/{case_id}/defense-dossier", response_model=DefenseDossier)
async def build_defense_dossier(
    case_id: int, session: AsyncSession = Depends(get_session)
) -> DefenseDossier:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    parties_result = await session.exec(select(Party).where(Party.case_id == case_id))
    documents_result = await session.exec(
        select(Document).where(Document.case_id == case_id).order_by(Document.uploaded_at)
    )

    party_summaries = [
        DefenseDossierParty(
            id=party.id,
            name=party.name,
            role=party.role,
            contact_email=party.contact_email,
        )
        for party in parties_result.all()
    ]

    document_summaries = [
        DefenseDossierDocument(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            description=document.description,
            uploaded_at=document.uploaded_at,
        )
        for document in documents_result.all()
    ]

    notes = (
        "Dossier automatique généré à partir des documents fournis."
        if document_summaries
        else "Aucun document fourni pour ce dossier pour le moment."
    )

    return DefenseDossier(
        case_id=case.id,
        generated_at=datetime.utcnow(),
        case_title=case.title,
        case_status=case.status,
        jurisdiction=case.jurisdiction,
        parties=party_summaries,
        documents=document_summaries,
        notes=notes,
    )


@app.get("/health", status_code=status.HTTP_200_OK)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
