from Sharepoint_Handler.Read_excel import read_excel_from_sharepoint
import math
from fastapi import  HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from Sharepoint_Handler.Write_on_excel_file import write_excel_to_sharepoint

class Fond(BaseModel):
    nom: str
    anciennete: str


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
    
def CreateFond(nom: str, anciennete: Optional[str] = None):
    df = read_excel_from_sharepoint()

    
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Impossible de lire le fichier Excel depuis SharePoint.",
        )

    df = df.iloc[:, :2].copy()
    df.columns = ["nom", "anciennete"]
    df = df.dropna(subset=["nom"])

    # Check for duplicates
    if df["nom"].astype(str).str.strip().str.lower().eq(nom.strip().lower()).any():
        raise HTTPException(
            status_code=409,
            detail=f"Le fond '{nom}' existe déjà.",
        )

    
    new_row = pd.DataFrame([{"nom": nom, "anciennete": anciennete}])
    df = pd.concat([df, new_row], ignore_index=True)

    success = write_excel_to_sharepoint(df)
    
    if not success:
        raise HTTPException(
            status_code=503,
            detail="Impossible de mettre à jour le fichier Excel sur SharePoint.",
        )

    df = read_excel_from_sharepoint()

    return Fond(nom=nom, anciennete=anciennete)

def DeleteFond(nom: str):
    df = read_excel_from_sharepoint()
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Impossible de lire le fichier Excel depuis SharePoint.",
        )

    df = df.iloc[:, :2].copy()
    df.columns = ["nom", "anciennete"]
    df = df.dropna(subset=["nom"])

    mask = df["nom"].astype(str).str.strip().str.lower().eq(nom.strip().lower())
    
    if not mask.any():
        raise HTTPException(
            status_code=404,
            detail=f"Le fond '{nom}' est introuvable.",
        )

    df = df.drop(df[df["nom"] == nom].index)

    
    success = write_excel_to_sharepoint(df)
    if not success:
        raise HTTPException(
            status_code=503,
            detail="Impossible de mettre à jour le fichier Excel sur SharePoint.",
        )

    return {"message": f"Le fond '{nom}' a été supprimé avec succès."}

