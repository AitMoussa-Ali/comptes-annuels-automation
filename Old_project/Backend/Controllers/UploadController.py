from typing import List, Optional

from fastapi import HTTPException, UploadFile, File
from pydantic import BaseModel

from Sharepoint_Handler.Upload import upload_file_to_sharepoint

# Labels used as SharePoint filenames (key = form field name, value = display/file label)
FILES_ANCIENNETE_A = {
    "fichier_vl_n":        "Fichier VL N",
    "fichier_vl_n_1":      "Fichier VL N-1",
    "balance_n_1":         "Balance N-1",
    "comptes_annuels_n_1": "Comptes annuels N-1",
}

FILES_ANCIENNETE_N = {
    "fichier_vl_n":           "Fichier VL N",
    "comptes_annuels":  "Comptes annuels vide",
}


class UploadResponse(BaseModel):
    success: bool
    fond_name: str
    uploaded_files: List[str]
    message: str


def _required_files(anciennete: str) -> dict:
    val = anciennete.strip().upper()
    if val == "A":
        return FILES_ANCIENNETE_A
    if val == "N":
        return FILES_ANCIENNETE_N
    raise HTTPException(
        status_code=400,
        detail=f"Valeur d'ancienneté invalide : '{anciennete}'. Valeurs acceptées : 'A' ou 'N'.",
    )


async def UploadFondFiles(
    fond_name: str,
    anciennete: str,
    fichier_vl_n: Optional[UploadFile] = File(...),
    fichier_vl_n_1: Optional[UploadFile] = File(...),
    balance_n_1: Optional[UploadFile] = File(...),
    comptes_annuels_n_1: Optional[UploadFile] = File(...),
    comptes_annuels: Optional[UploadFile] = File(...),
) -> UploadResponse:

    required = _required_files(anciennete)

    provided: dict[str, Optional[UploadFile]] = {
        "fichier_vl_n":           fichier_vl_n,
        "fichier_vl_n_1":         fichier_vl_n_1,
        "balance_n_1":            balance_n_1,
        "comptes_annuels_n_1":    comptes_annuels_n_1,
        "comptes_annuels": comptes_annuels,
    }

    # Validate all required files are present
    missing = [
        FILES_ANCIENNETE_A.get(key) or FILES_ANCIENNETE_N.get(key, key)
        for key in required
        if provided.get(key) is None
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Fichiers manquants pour le fonds '{fond_name}' (ancienneté {anciennete}) : {', '.join(missing)}",
        )

    # Upload each required file to SharePoint
    uploaded: List[str] = []
    failed: List[str] = []

    for field_key, label in required.items():
        upload_file: UploadFile = provided[field_key]
        content = await upload_file.read()
        filename = f"{label}{_extension(upload_file.filename)}"

        success = upload_file_to_sharepoint(
            filename=filename,
            content=content,
            fond_name=fond_name,
        )
        if success:
            uploaded.append(filename)
        else:
            failed.append(filename)

    if failed:
        raise HTTPException(
            status_code=502,
            detail=f"Échec de l'upload vers SharePoint pour : {', '.join(failed)}",
        )

    return UploadResponse(
        success=True,
        fond_name=fond_name,
        uploaded_files=uploaded,
        message=f"{len(uploaded)} fichier(s) uploadé(s) avec succès pour le fonds '{fond_name}'.",
    )


def _extension(filename: Optional[str]) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ""
