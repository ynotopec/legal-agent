from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
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

app = FastAPI(title="Legal Case Management API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.post("/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(*, payload: CaseCreate, session: AsyncSession = Depends(get_session)) -> CaseRead:
    case = Case.from_orm(payload)
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@app.get("/cases", response_model=List[CaseRead])
async def list_cases(session: AsyncSession = Depends(get_session)) -> List[CaseRead]:
    result = await session.exec(select(Case))
    return result.all()


@app.get("/cases/{case_id}", response_model=CaseRead)
async def get_case(case_id: int, session: AsyncSession = Depends(get_session)) -> CaseRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@app.patch("/cases/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: int, *, payload: CaseUpdate, session: AsyncSession = Depends(get_session)
) -> CaseRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)
    case.updated_at = datetime.utcnow()

    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@app.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int, session: AsyncSession = Depends(get_session)) -> None:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    await session.delete(case)
    await session.commit()


@app.post("/cases/{case_id}/parties", response_model=PartyRead, status_code=status.HTTP_201_CREATED)
async def add_party(
    case_id: int, *, payload: PartyCreate, session: AsyncSession = Depends(get_session)
) -> PartyRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    party = Party.from_orm(payload)
    session.add(party)
    await session.commit()
    await session.refresh(party)
    return party


@app.get("/cases/{case_id}/parties", response_model=List[PartyRead])
async def list_parties(case_id: int, session: AsyncSession = Depends(get_session)) -> List[PartyRead]:
    result = await session.exec(select(Party).where(Party.case_id == case_id))
    return result.all()


@app.post("/cases/{case_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
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

    document = Document.from_orm(payload)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@app.get("/cases/{case_id}/documents", response_model=List[DocumentRead])
async def list_documents(case_id: int, session: AsyncSession = Depends(get_session)) -> List[DocumentRead]:
    result = await session.exec(select(Document).where(Document.case_id == case_id))
    return result.all()


@app.post("/cases/{case_id}/hearings", response_model=HearingRead, status_code=status.HTTP_201_CREATED)
async def add_hearing(
    case_id: int, *, payload: HearingCreate, session: AsyncSession = Depends(get_session)
) -> HearingRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    hearing = Hearing.from_orm(payload)
    session.add(hearing)
    await session.commit()
    await session.refresh(hearing)
    return hearing


@app.get("/cases/{case_id}/hearings", response_model=List[HearingRead])
async def list_hearings(case_id: int, session: AsyncSession = Depends(get_session)) -> List[HearingRead]:
    result = await session.exec(select(Hearing).where(Hearing.case_id == case_id))
    return result.all()


@app.post("/cases/{case_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def add_task(
    case_id: int, *, payload: TaskCreate, session: AsyncSession = Depends(get_session)
) -> TaskRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case ID mismatch")

    task = Task.from_orm(payload)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@app.get("/cases/{case_id}/tasks", response_model=List[TaskRead])
async def list_tasks(case_id: int, session: AsyncSession = Depends(get_session)) -> List[TaskRead]:
    result = await session.exec(select(Task).where(Task.case_id == case_id))
    return result.all()


@app.post("/cases/{case_id}/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document_file(
    case_id: int,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    case = await session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    document = Document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        description="Uploaded via multipart",
        case_id=case_id,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@app.get("/cases/{case_id}/defense-dossier", response_model=DefenseDossier)
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
