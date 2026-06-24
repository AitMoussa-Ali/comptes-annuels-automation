from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional
from Controllers.UploadController import UploadController

router = APIRouter(prefix="/upload", tags=["uploader"])

@router.post("/")
async def upload_files(
    anciennete: str = Form(...),
    fichier_vl_n: UploadFile = File(...),
    comptes_annuels: UploadFile = File(...),
    fichier_vl_n_1: Optional[UploadFile] = File(None),
):
    return await UploadController(anciennete=anciennete, fichier_vl_n=fichier_vl_n, fichier_vl_n_1=fichier_vl_n_1, comptes_annuels=comptes_annuels)