from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


class CaseBase(SQLModel):
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    jurisdiction: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="draft", max_length=50)


class Case(CaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    parties: List["Party"] = Relationship(back_populates="case")
    documents: List["Document"] = Relationship(back_populates="case")
    hearings: List["Hearing"] = Relationship(back_populates="case")
    tasks: List["Task"] = Relationship(back_populates="case")


class CaseCreate(CaseBase):
    pass


class CaseRead(CaseBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CaseUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    jurisdiction: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = Field(default=None, max_length=50)


class PartyBase(SQLModel):
    name: str
    role: str
    contact_email: Optional[str] = None


class Party(PartyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")

    case: Optional[Case] = Relationship(back_populates="parties")


class PartyCreate(PartyBase):
    case_id: int


class PartyRead(PartyBase):
    id: int
    case_id: int


class DocumentBase(SQLModel):
    filename: str
    content_type: str
    description: Optional[str] = None


class Document(DocumentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    case: Optional[Case] = Relationship(back_populates="documents")


class DocumentCreate(DocumentBase):
    case_id: int


class DocumentRead(DocumentBase):
    id: int
    case_id: int
    uploaded_at: datetime


class HearingBase(SQLModel):
    title: str
    scheduled_at: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class Hearing(HearingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")

    case: Optional[Case] = Relationship(back_populates="hearings")


class HearingCreate(HearingBase):
    case_id: int


class HearingRead(HearingBase):
    id: int
    case_id: int


class TaskBase(SQLModel):
    title: str
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    completed: bool = False


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    case: Optional[Case] = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    case_id: int


class TaskRead(TaskBase):
    id: int
    case_id: int
    created_at: datetime


class DefenseDossierParty(SQLModel):
    id: int
    name: str
    role: str
    contact_email: Optional[str] = None


class DefenseDossierDocument(SQLModel):
    id: int
    filename: str
    content_type: str
    description: Optional[str] = None
    uploaded_at: datetime


class DefenseDossier(SQLModel):
    case_id: int
    generated_at: datetime
    case_title: str
    case_status: str
    jurisdiction: Optional[str] = None
    parties: List[DefenseDossierParty] = Field(default_factory=list)
    documents: List[DefenseDossierDocument] = Field(default_factory=list)
    notes: Optional[str] = None
