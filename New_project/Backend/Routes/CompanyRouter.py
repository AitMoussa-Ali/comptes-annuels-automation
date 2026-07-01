"""
routers/company_router.py
=========================
Routes REST pour les sociétés de gestion.

  POST   /companies/              → CreateCompany
  GET    /companies/              → GetCompanies     (paginé)
  GET    /companies/{company_id}  → GetCompanyById
  PATCH  /companies/{company_id}  → UpdateCompany
  DELETE /companies/{company_id}  → DeleteCompany
"""

import uuid
from fastapi import APIRouter, Depends, Query
from fastapi import Form

from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from Controllers.CompanyController import (
    CreateCompany,
    GetCompanies,
    GetCompanyById,
    UpdateCompany,
    DeleteCompany,
)
from Schemas.CompanySchema import (
    CompanyCreate,
    CompanyResponse,
    CompanyDeleteUpdated,
    PaginatedCompanies,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    return CreateCompany(payload=payload, db=db)


@router.get("/", response_model=PaginatedCompanies)
def get_companies(
    page:      int = Query(default=1,  ge=1,  description="Numéro de page"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items par page"),
    search: str = Query(default="", description="Terme de recherche pour filtrer les sociétés"),
    db: AsyncSession = Depends(get_db),
):
    return GetCompanies(db=db, page=page, page_size=page_size, search=search)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return GetCompanyById(company_id=company_id, db=db)


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    return UpdateCompany(company_id=company_id, payload=payload, db=db)


@router.delete("/{company_id}", response_model=CompanyDeleteUpdated)
def delete_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return DeleteCompany(company_id=company_id, db=db)
