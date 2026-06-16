from Sharepoint_Handler.Read_excel import read_excel_from_sharepoint
import math
from fastapi import  HTTPException
from pydantic import BaseModel
from typing import List, Optional

class Fond(BaseModel):
    nom: str
    anciennete: Optional[str] = None


class FondsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[Fond]
    next_page : Optional[str] = None
    previous_page : Optional[str] = None


def GetFonds(search, page, page_size):    
    df = read_excel_from_sharepoint()
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Impossible de lire le fichier Excel depuis SharePoint.",
        )
    # Take first two columns regardless of their header names in the Excel file
    df = df.iloc[:, :2].copy()
    df.columns = ["nom", "anciennete"]
    df = df.dropna(subset=["nom"])
    # Search filter
    if search:
        df = df[df["nom"].astype(str).str.contains(search, case=False, na=False)]
    total = len(df)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]
    def _to_str(val) -> Optional[str]:
        if val is None:
            return None
        try:
            if math.isnan(float(val)):
                return None
        except (TypeError, ValueError):
            pass
        return str(val)
    fonds = [
        Fond(nom=str(row["nom"]), anciennete=_to_str(row["anciennete"]))
        for _, row in page_df.iterrows()
    ]
    next_page = (
    f"/api/fonds?page={page + 1}&page_size={page_size}&search={search}"
    if page < total_pages else None
    )
    previous_page = (
    f"/api/fonds?page={page - 1}&page_size={page_size}&search={search}"
    if page > 1 else None
    )
    return FondsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        data=fonds,
        next_page=next_page,
        previous_page=previous_page
    )