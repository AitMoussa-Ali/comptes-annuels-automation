from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional
from Controllers.GenerateController import generate_comptes_annuels

router = APIRouter(prefix="/generate", tags=["Generate"])

@router.post("/")
async def generate(
    anciennete: str = Form(...),
    fichier_vl_n: UploadFile = File(...),
    comptes_annuels: UploadFile = File(...),
    fichier_vl_n_1: Optional[UploadFile] = File(None),
):
    return await generate_comptes_annuels(
        anciennete=anciennete,
        fichier_vl_n=fichier_vl_n,
        comptes_annuels=comptes_annuels,
        fichier_vl_n_1=fichier_vl_n_1,
    )