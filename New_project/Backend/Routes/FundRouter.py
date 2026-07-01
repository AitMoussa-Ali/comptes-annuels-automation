"""
routers/fund_router.py
======================
Routes REST pour les fonds d'investissement.

  POST   /funds/                          → CreateFund
  GET    /funds/                          → GetFunds         (paginé, filtre company)
  GET    /funds/{fund_id}                 → GetFundById
  PATCH  /funds/{fund_id}                 → UpdateFund
  DELETE /funds/{fund_id}                 → DeleteFund

  GET    /companies/{company_id}/funds/   → GetFunds filtrés par société
"""

import uuid
from typing import Optional
from fastapi import Form
 
from fastapi import APIRouter, Depends, Query

from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from Controllers.FundController import (
    CreateFund,
    GetFunds,
    GetFundById,
    UpdateFund,
    DeleteFund,
)
from Models.FundModel import AncientStatus
from Schemas.FundSchema import (
    FundCreate,
    FundResponse,
    FundDeleteUpdated,
    PaginatedFunds,
)

router = APIRouter(tags=["Funds"])


# ── Routes /funds ──────────────────────────────────────────────────────────────

@router.post("/companies/{company_id}/funds/", response_model=FundResponse, status_code=201)
async def create_fund(
    company_id: uuid.UUID,
    payload: FundCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crée un fonds rattaché à la société `company_id`."""
    return CreateFund(
        payload=payload,
        company_id=company_id,
        db=db,
    )


@router.get("/funds/", response_model=PaginatedFunds)
async def get_funds(
    search: str = None,
    page:       int                    = Query(default=1,   ge=1,  description="Numéro de page"),
    page_size:  int                    = Query(default=10,  ge=1, le=100, description="Items par page"),
    company_id: Optional[uuid.UUID]    = Query(default=None, description="Filtrer par société"),
    db: AsyncSession = Depends(get_db),
):
    """Retourne tous les fonds (filtrables par société)."""
    return GetFunds(db=db, page=page, page_size=page_size, company_id=company_id, search=search)


@router.get("/companies/{company_id}/funds/", response_model=PaginatedFunds)
async def get_funds_by_company(
    company_id: uuid.UUID,
    page:      int = Query(default=1,  ge=1,  description="Numéro de page"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items par page"),
    db: AsyncSession = Depends(get_db),
):
    """Retourne tous les fonds d'une société donnée."""
    return GetFunds(db=db, page=page, page_size=page_size, company_id=company_id)


@router.get("/funds/{fund_id}", response_model=FundResponse)
async def get_fund(
    fund_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return GetFundById(fund_id=fund_id, db=db)


@router.patch("/funds/{fund_id}", response_model=FundResponse)
async def update_fund(
    fund_id: uuid.UUID,
    payload: FundCreate,
    company_id: uuid.UUID = Query(..., description="Nouvelle société de gestion"),
    db: AsyncSession = Depends(get_db),
):
    return UpdateFund(fund_id=fund_id, payload=payload, company_id=company_id, db=db)


@router.delete("/funds/{fund_id}", response_model=FundDeleteUpdated)
async def delete_fund(
    fund_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return DeleteFund(fund_id=fund_id, db=db)