"""
CompanyController.py
====================
CRUD complet pour l'entité Company.

Opérations :
  - CreateCompany    → POST   /companies/
  - GetCompanies     → GET    /companies/          (paginé)
  - GetCompanyById   → GET    /companies/{id}
  - UpdateCompany    → PATCH  /companies/{id}
  - DeleteCompany    → DELETE /companies/{id}
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from Models.CompanyModel import Company
from Schemas.CompanySchema import (
    CompanyCreate,
    CompanyResponse,
    CompanyDeleteUpdated,
    PaginatedCompanies,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_pagination(
    total_items: int,
    page: int,
    page_size: int,
    items: list[Company],
) -> PaginatedCompanies:
    total_pages = max(1, math.ceil(total_items / page_size))
    return PaginatedCompanies(
        items=[CompanyResponse.model_validate(c) for c in items],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
    )


def _get_or_404(db: AsyncSession, company_id: uuid.UUID) -> Company:
    result = db.execute(
        select(Company).where(Company.company_id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id '{company_id}' not found.",
        )
    return company


# ─── Controllers ──────────────────────────────────────────────────────────────

def CreateCompany(
    payload: CompanyCreate,
    db: AsyncSession,
) -> CompanyResponse:
    """
    Crée une nouvelle société de gestion.
    Retourne 409 si le nom existe déjà.
    """
    # Unicité du nom
    existing = db.execute(
        select(Company).where(Company.company_name == payload.company_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company '{payload.company_name}' already exists.",
        )

    company = Company(
        company_name=payload.company_name,
        company_creation_date=payload.company_creation_date,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return CompanyResponse.model_validate(company)


def GetCompanies(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
) -> PaginatedCompanies:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be >= 1.",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be between 1 and 100.",
        )

    # Filtre de recherche (insensible à la casse)
    search_filter = (
        Company.company_name.ilike(f"%{search}%")
        if search and search.strip()
        else None
    )

    # Total — filtré si recherche active
    count_query = select(func.count(Company.company_id))
    if search_filter is not None:
        count_query = count_query.where(search_filter)
    count_result = db.execute(count_query)
    total_items = count_result.scalar_one()

    # Données — filtrées + paginées
    offset = (page - 1) * page_size
    data_query = select(Company).order_by(Company.company_name).offset(offset).limit(page_size)
    if search_filter is not None:
        data_query = data_query.where(search_filter)
    result = db.execute(data_query)
    companies = result.scalars().all()

    return _build_pagination(total_items, page, page_size, companies)

def GetCompanyById(
    company_id: uuid.UUID,
    db: AsyncSession,
) -> CompanyResponse:
    """Retourne une société par son UUID. 404 si inexistante."""
    company = _get_or_404(db, company_id)
    return CompanyResponse.model_validate(company)


def UpdateCompany(
    company_id: uuid.UUID,
    payload: CompanyCreate,
    db: AsyncSession,
) -> CompanyResponse:
    """
    Met à jour le nom et/ou la date de création d'une société.
    Retourne 409 si le nouveau nom est déjà pris.
    """
    company = _get_or_404(db, company_id)

    # Unicité du nouveau nom (hors soi-même)
    if payload.company_name != company.company_name:
        existing = db.execute(
            select(Company).where(Company.company_name == payload.company_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Company name '{payload.company_name}' is already taken.",
            )

    company.company_name = payload.company_name
    company.company_creation_date = payload.company_creation_date
    company.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(company)
    return CompanyResponse.model_validate(company)


def DeleteCompany(
    company_id: uuid.UUID,
    db: AsyncSession,
) -> CompanyDeleteUpdated:
    """
    Supprime une société et tous ses fonds (cascade défini dans le modèle).
    Retourne le nom de la société supprimée.
    """
    company = _get_or_404(db, company_id)
    name = company.company_name
    db.delete(company)
    db.commit()
    return CompanyDeleteUpdated(company_name=name)