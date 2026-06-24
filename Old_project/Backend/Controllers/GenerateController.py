import asyncio
import io
import os
import tempfile
import time

import pythoncom
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from Data_manipulation.Data_extraction import Data_extraction
from Data_manipulation.Excel_macros import Excel_macros
from Data_manipulation.Reading_files import Reading_files


def _run_excel_generation(
    tmp_path: str,
    anciennete: str,
    balance_n,
    inventaire_n,
    pvmv,
    balance_n_1=None,
    inventaire_n_1=None,
) -> bytes:
    # COM doit être initialisé dans chaque thread qui utilise win32com
    pythoncom.CoInitialize()
    try:
        rf = Reading_files()
        workbook, excel = rf.open_excel_file(tmp_path)
        macros = Excel_macros(workbook)

        macros.effacer_donnees_et_mise_en_forme()

        macros.paste_df_to_sheet("Balance",    balance_n)
        macros.paste_df_to_sheet("Inventaire", inventaire_n)
        macros.paste_df_to_sheet("PVMV",       pvmv)

        if anciennete == "A":
            macros.paste_df_to_sheet("Balance N-1",    balance_n_1)
            macros.paste_df_to_sheet("Inventaire N-1", inventaire_n_1)
            macros.convertir_colonne_a_texte()
        elif anciennete == "N":
            macros.convertir_colonne_a_texte()

        workbook.Save()
        workbook.Close(SaveChanges=True)
        excel.Quit()

        time.sleep(1)

        with open(tmp_path, "rb") as f:
            return f.read()

    finally:
        pythoncom.CoUninitialize()
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def generate_comptes_annuels(
    anciennete: str,
    fichier_vl_n: UploadFile,
    comptes_annuels: UploadFile,
    fichier_vl_n_1: UploadFile = None,
):
    anciennete = anciennete.strip().upper()

    # ── 1. Lire les fichiers uploadés en mémoire (async, libère l'event loop)
    vl_n_bytes    = await fichier_vl_n.read()
    comptes_bytes = await comptes_annuels.read()
    vl_n_1_bytes  = await fichier_vl_n_1.read() if fichier_vl_n_1 else None

    # ── 2. Extraire les DataFrames
    extractor = Data_extraction(
        fichier_vl     = io.BytesIO(vl_n_bytes),
        fichier_vl_n_1 = io.BytesIO(vl_n_1_bytes) if vl_n_1_bytes else None,
    )
    balance_n, inventaire_n, pvmv = extractor.extracting_data_n()

    balance_n_1 = inventaire_n_1 = None
    if anciennete == "A":
        balance_n_1, inventaire_n_1 = extractor.extracting_data_n_1()

    # ── 3. Écrire le template sur disque (win32com nécessite un vrai path)
    with tempfile.NamedTemporaryFile(suffix=".xlsm", delete=False) as tmp:
        tmp.write(comptes_bytes)
        tmp_path = tmp.name

    # ── 4. Exécuter win32com dans un thread séparé pour ne pas bloquer l'event loop
    try:
        result_bytes = await asyncio.to_thread(
            _run_excel_generation,
            tmp_path,
            anciennete,
            balance_n,
            inventaire_n,
            pvmv,
            balance_n_1,
            inventaire_n_1,
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Erreur génération Excel : {str(e)}")

    if not result_bytes:
        raise HTTPException(status_code=500, detail="Le fichier généré est vide.")

    # ── 5. Retourner le fichier rempli
    return StreamingResponse(
        io.BytesIO(result_bytes),
        media_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        headers={"Content-Disposition": "attachment; filename=comptes_annuels_rempli.xlsm"},
    )
