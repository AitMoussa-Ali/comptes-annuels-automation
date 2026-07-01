"""
FundController.py
=================
CRUD complet pour l'entité Fund.

Opérations :
  - CreateFund      → POST   /funds/
  - GetFunds        → GET    /funds/           (paginé, filtrable par company)
  - GetFundById     → GET    /funds/{id}
  - UpdateFund      → PATCH  /funds/{id}
  - DeleteFund      → DELETE /funds/{id}
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from Models.FundModel import Fund, AncientStatus
from Models.CompanyModel import Company
from Schemas.FundSchema import (
    FundCreate,
    FundResponse,
    FundDeleteUpdated,
    PaginatedFunds,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_pagination(
    total_items: int,
    page: int,
    page_size: int,
    items: list[Fund],
) -> PaginatedFunds:
    total_pages = max(1, math.ceil(total_items / page_size))
    return PaginatedFunds(
        items=[FundResponse.model_validate(f) for f in items],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
    )


def _get_or_404(db: AsyncSession, fund_id: uuid.UUID) -> Fund:
    result = db.execute(
        select(Fund)
        .options(selectinload(Fund.company))
        .where(Fund.fund_id == fund_id)
    )
    fund = result.scalar_one_or_none()
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fund with id '{fund_id}' not found.",
        )
    return fund


def _get_company_or_404(db: AsyncSession, company_id: uuid.UUID) -> Company:
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


def _validate_pagination(page: int, page_size: int) -> None:
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


# ─── Controllers ──────────────────────────────────────────────────────────────

def CreateFund(
    company_id: uuid.UUID,
    db: AsyncSession,
    payload: FundCreate,
) -> FundResponse:
    """
    Crée un nouveau fonds rattaché à une société de gestion.

    Paramètres
    ----------
    payload     : nom + date de création
    company_id  : UUID de la société parente (doit exister)
    anciennete  : "A" = fonds avec N-1, "N" = premier exercice (défaut)
    bilingue    : rapport bilingue FR/EN (défaut False)

    Retourne 404 si la société n'existe pas.
    Retourne 409 si le nom de fonds est déjà pris.
    """
    # Vérifier que la société existe
    _get_company_or_404(db, company_id)

    # Unicité du nom
    existing = db.execute(
        select(Fund).where(Fund.fund_name == payload.fund_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Fund '{payload.fund_name}' already exists.",
        )

    fund = Fund(
        fund_name=payload.fund_name,
        fund_creation_date=payload.fund_creation_date,
        fund_anciente=payload.anciennete,
        fund_bilingue=payload.bilingue,
        company_id=company_id,
    )
    db.add(fund)
    db.commit()

    # Recharger avec la relation company pour FundResponse.company_name
    result = db.execute(
        select(Fund)
        .options(selectinload(Fund.company))
        .where(Fund.fund_id == fund.fund_id)
    )
    
    fund = result.scalar_one()
    return FundResponse.model_validate(fund)


def GetFunds(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    company_id: uuid.UUID | None = None,
    search: str | None = None,
) -> PaginatedFunds:
    _validate_pagination(page, page_size)

    base_query = select(Fund).options(selectinload(Fund.company))
    count_query = select(func.count(Fund.fund_id))

    if company_id:
        base_query = base_query.where(Fund.company_id == company_id)
        count_query = count_query.where(Fund.company_id == company_id)

    if search:
        filter_search = or_(
            Fund.fund_name.ilike(f"%{search}%"),
            Company.company_name.ilike(f"%{search}%")
        )

        base_query = (
            base_query
            .join(Fund.company)
            .where(filter_search)
        )

        count_query = (
            count_query
            .join(Fund.company)
            .where(filter_search)
        )
        
    total_items = db.execute(count_query).scalar_one()

    offset = (page - 1) * page_size

    funds = (
        db.execute(
            base_query
            .order_by(Fund.fund_name)
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return _build_pagination(total_items, page, page_size, funds)

def GetFundById(
    fund_id: uuid.UUID,
    db: AsyncSession,
) -> FundResponse:
    """Retourne un fonds par son UUID. 404 si inexistant."""
    fund = _get_or_404(db, fund_id)
    return FundResponse.model_validate(fund)


def UpdateFund(
    fund_id: uuid.UUID,
    payload: FundCreate,
    company_id: uuid.UUID,   # ← ajouter
    db: AsyncSession,
) -> FundResponse:
    fund = _get_or_404(db, fund_id)

    if payload.fund_name != fund.fund_name:
        existing = db.execute(select(Fund).where(Fund.fund_name == payload.fund_name))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"Fund name '{payload.fund_name}' is already taken.")
        fund.fund_name = payload.fund_name

    # Changement de société
    if company_id != fund.company_id:
        _get_company_or_404(db, company_id)  # vérifie que la nouvelle société existe
        fund.company_id = company_id

    fund.fund_creation_date = payload.fund_creation_date
    if payload.anciennete is not None:
        fund.fund_anciente = payload.anciennete
    if payload.bilingue is not None:
        fund.fund_bilingue = payload.bilingue
    fund.updated_at = datetime.utcnow()

    db.commit()
    result = db.execute(
        select(Fund).options(selectinload(Fund.company)).where(Fund.fund_id == fund.fund_id)
    )
    fund = result.scalar_one()
    return FundResponse.model_validate(fund)

def DeleteFund(
    fund_id: uuid.UUID,
    db: AsyncSession,
) -> FundDeleteUpdated:
    """
    Supprime un fonds.
    Retourne le nom du fonds supprimé.
    """
    fund = _get_or_404(db, fund_id)
    name = fund.fund_name
    db.delete(fund)
    db.commit()
    return FundDeleteUpdated(fund_name=name)