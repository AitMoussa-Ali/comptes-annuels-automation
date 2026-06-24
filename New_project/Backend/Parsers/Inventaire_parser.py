import numpy as np

async def parser_inventaire(x1):

    # ✅ Find the sheet name regardless of spacing/casing
    # xl = pd.ExcelFile(file.file)
    sheet_name = next(
        (s for s in x1.sheet_names if s.strip().lower() == "inventaire"),
        None
    )

    if sheet_name is None:
        raise ValueError(f"No 'Inventaire' sheet found. Available sheets: {x1.sheet_names}")

    inventaire_df = x1.parse(sheet_name=sheet_name, header=None)

    total_rows = inventaire_df[inventaire_df.iloc[:, 1] == "Total"].index
    print("-----------------")
    print(total_rows[0])
    if not total_rows.empty:
        print("condition")
        df = inventaire_df.iloc[:total_rows[0]-1]
    else:
        df = inventaire_df

    df = df.iloc[15:, 0:15].reset_index(drop=True)

    df.columns = [
        'G ou I','Code_titre', 'Libellé', 'Quantité', 'Prix de revient unitaire',
        'Estimation unitaire', 'Origine du cours', 'Prix de revient',
        'Intérêts ou dividendes capitalisés', 'Prix de revient global',
        'Valeur estimation hors coupon', 'Value potentielle',
        'Coupon couru ou divedendes', 'Valeur estimation coupon inclus',
        'actif net'
    ]

    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
    print("Parsed Inventaire !!!")
    return df.to_dict(orient="records")

