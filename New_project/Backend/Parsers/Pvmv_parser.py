import pandas as pd
import numpy as np


async def parser_pvmv(x1):

    # ✅ Find the sheet name regardless of spacing/casing
    
    # x1 = pd.ExcelFile(file.file)
    sheet_name = next(
        (s for s in x1.sheet_names if s.strip().lower() == "pvmv"),
        None
    )

    if sheet_name is None:
        raise ValueError(f"No 'PVMV' sheet found. Available sheets: {x1.sheet_names}")

    pvmv_df = x1.parse(sheet_name=sheet_name, header=None)

    total_rows = pvmv_df[pvmv_df.iloc[:, 1] == "TOTAL"].index

    if not total_rows.empty:
        df = pvmv_df.iloc[:total_rows[0] + 1]
    else:
        df = pvmv_df

    df = df.iloc[5:, 1:19].reset_index(drop=True)

    df.columns = [
        'TITRE', 'LIBELLE', 'DATE OPE', 'ACHATS_QTE', 'ACHATS_PR_UNITAIRE',
        'ACHATS_PR_OPERATION', 'VENTES_QTE', 'VENTES_PV_UNITAIRE', 'VENTES_PV_OPERATION',
        'VENTES_PR_OPERATION', 'SOLDES_QUANTITE', 'SOLDES_PR_CUMULE', 'SOLDES_PR_UNIT_MOYEN',
        'PLUS_VALUES_REALISEES', 'MOINS_VALUES_REALISEES', 'PRIX_DE_VENTE_DE_REVIENT',
        'SOMMES_DES_PLUS_OU_MOINS_VALUES', 'CONTROLE'
    ]

    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
    print("Parsed Pvmv !!!")
    return df.to_dict(orient="records")
