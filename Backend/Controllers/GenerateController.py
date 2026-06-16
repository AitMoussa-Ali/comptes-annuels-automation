import io
import tempfile
import os
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from Data_manipulation.Data_extraction import Data_extraction
from Data_manipulation.Excel_macros import Excel_macros
from Data_manipulation.Reading_files import Reading_files


async def generate_comptes_annuels(
    anciennete: str,
    fichier_vl_n: UploadFile,
    comptes_annuels: UploadFile,
    fichier_vl_n_1: UploadFile = None,
):
    anciennete = anciennete.strip().upper()

    # ── 1. Lire les fichiers uploadés en mémoire
    vl_n_bytes      = await fichier_vl_n.read()
    comptes_bytes   = await comptes_annuels.read()
    vl_n_1_bytes    = await fichier_vl_n_1.read() if fichier_vl_n_1 else None

    # ── 2. Extraire les DataFrames
    extractor = Data_extraction(
        fichier_vl      = io.BytesIO(vl_n_bytes),
        fichier_vl_n_1  = io.BytesIO(vl_n_1_bytes) if vl_n_1_bytes else None,
    )
    balance_n, inventaire_n, pvmv = extractor.extracting_data_n()

    if anciennete == "A":
        balance_n_1, inventaire_n_1 = extractor.extracting_data_n_1()

    # ── 3. Sauvegarder comptes_annuels dans un fichier temporaire
    #       (win32com a besoin d'un vrai path sur disque)
    with tempfile.NamedTemporaryFile(suffix=".xlsm", delete=False) as tmp:
        tmp.write(comptes_bytes)
        tmp_path = tmp.name

    try:
        # ── 4. Ouvrir via win32com et coller les données
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
            # macros.recreer_code_inventaire()

        # ── 5. Sauvegarder et lire le résultat
        workbook.Save()
        workbook.Close(SaveChanges=True)
        excel.Quit()

        with open(tmp_path, "rb") as f:
            result_bytes = f.read()

    finally:
        os.unlink(tmp_path)  # Nettoyer le fichier temporaire

    # ── 6. Retourner le fichier rempli en téléchargement
    return StreamingResponse(
        io.BytesIO(result_bytes),
        media_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        headers={"Content-Disposition": "attachment; filename=comptes_annuels_rempli.xlsm"}
    )
    