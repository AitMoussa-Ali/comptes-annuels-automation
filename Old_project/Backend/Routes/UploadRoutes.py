from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from Controllers.UploadController import UploadResponse, UploadFondFiles

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=UploadResponse)
async def upload_fond_files(
    fond_name: str = Form(..., description="Nom du fonds sélectionné"),
    anciennete: str = Form(..., description="Ancienneté du fonds : 'A' ou 'N'"),
    fichier_vl_n: Optional[UploadFile] = File(None, description="Fichier VL N (requis pour A et N)"),
    fichier_vl_n_1: Optional[UploadFile] = File(None, description="Fichier VL N-1 (requis pour A uniquement)"),
    balance_n_1: Optional[UploadFile] = File(None, description="Balance N-1 (requis pour A uniquement)"),
    comptes_annuels_n_1: Optional[UploadFile] = File(None, description="Comptes annuels N-1 (requis pour A uniquement)"),
    comptes_annuels_vide: Optional[UploadFile] = File(None, description="Comptes résultats vide (requis pour N uniquement)"),
):
    return await UploadFondFiles(
        fond_name=fond_name,
        anciennete=anciennete,
        fichier_vl_n=fichier_vl_n,
        fichier_vl_n_1=fichier_vl_n_1,
        balance_n_1=balance_n_1,
        comptes_annuels_n_1=comptes_annuels_n_1,
        comptes_annuels=comptes_annuels_vide,
    )
