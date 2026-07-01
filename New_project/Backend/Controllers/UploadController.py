import io

from fastapi import UploadFile

from Data_manipulation.Data_extraction import Data_extraction
from Controllers.BilanController import BilanController
from Controllers.TextExtractionController import PdfToDictController
async def UploadController(
    anciennete: str,
    fichier_vl_n: UploadFile,
    comptes_annuels: UploadFile,
    fichier_vl_n_1: UploadFile = None,
):
    anciennete = anciennete.strip().upper()

    # ── 1. Lire les fichiers uploadés en mémoire (async, libère l'event loop)
    print("reading file N ")
    vl_n_bytes    = await fichier_vl_n.read()
    
    print("reading file N _ 1")
    vl_n_1_bytes  = await fichier_vl_n_1.read() if fichier_vl_n_1 else None

    # ── 2. Extraire les DataFrames
    extractor = Data_extraction(
        fichier_vl     = io.BytesIO(vl_n_bytes),
        fichier_vl_n_1 = io.BytesIO(vl_n_1_bytes) if vl_n_1_bytes else None,
    )
    result_n = await extractor.extracting_data_n()

    result_n_1 = None
    if anciennete == "A":
        result_n_1 = await extractor.extracting_data_n_1()

    pdf_bytes = await comptes_annuels.read()
    texts = await PdfToDictController(pdf_bytes)
    
    result = {
        "N" : result_n,
        "N_1" : result_n_1,
        "Data extracted" : texts
    }
    
    
    return result
