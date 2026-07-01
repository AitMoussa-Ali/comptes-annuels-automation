from pydantic import BaseModel, field_validator
from datetime import date, datetime
from uuid import UUID
from fastapi import Form

def _parse_date(v) -> date:
    """
    Accepte les formats :
      DD-MM-YYYY   →  25-05-2021
      DD/MM/YYYY   →  25/05/2021
      YYYY-MM-DD   →  2021-05-25  (ISO standard, déjà géré par Pydantic)
    """
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

class CompanyCreate(BaseModel):
    company_name : str 
    company_creation_date : date 
    
    @field_validator("company_creation_date", mode="before")
    @classmethod
    def parse_company_creation_date(cls, v):
        return _parse_date(v)
    
class CompanyResponse(BaseModel):
    company_id: UUID
    company_name: str
    company_creation_date: date

    model_config = {
        "from_attributes": True
    }
    
class PaginatedCompanies(BaseModel):
    items: list[CompanyResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    next_page: int | None
    previous_page: int | None

class CompanyDeleteUpdated(BaseModel):
    company_name : str
    