from pydantic import BaseModel, field_validator
from datetime import date, datetime
from uuid import UUID
from Models.FundModel import AncientStatus


def _parse_date(v) -> date:
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        v = v.strip()
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                continue
        raise ValueError(
            f"Invalid date format '{v}'. "
            "Expected DD-MM-YYYY, DD/MM/YYYY or YYYY-MM-DD."
        )
    raise ValueError(f"Cannot parse date from type {type(v).__name__}.")


class FundCreate(BaseModel):
    fund_name: str
    fund_creation_date: date
    anciennete: AncientStatus
    bilingue: bool = False

    @field_validator("fund_creation_date", mode="before")
    @classmethod
    def parse_fund_creation_date(cls, v):
        return _parse_date(v)


class FundResponse(BaseModel):
    fund_name: str
    fund_id: UUID
    fund_creation_date: date
    fund_anciente: str
    fund_bilingue: bool
    company_name: str
    company_id: UUID
    model_config = {"from_attributes": True}


class PaginatedFunds(BaseModel):
    items: list[FundResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    next_page: int | None
    previous_page: int | None


class FundDeleteUpdated(BaseModel):
    fund_name: str