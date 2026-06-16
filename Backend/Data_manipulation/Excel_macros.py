import pandas as pd
from Data_manipulation.Reading_files import Reading_files

class Excel_macros:

    def __init__(self, workbook):
        self.workbook = workbook
        self.rf = Reading_files()

    def paste_df_to_sheet(self, sheet_name, df):
        ws = self.rf.get_sheet(self.workbook, sheet_name)
        ws.Cells.Clear()

        df_clean = df.where(pd.notna(df), other=None)
        for col in df_clean.columns:
            if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].dt.strftime("%d/%m/%Y")

        rows, cols = df_clean.shape
        rng = ws.Range(ws.Cells(1, 1), ws.Cells(rows, cols))
        rng.Value = df_clean.values.tolist()
        print(f"'{sheet_name}' collé")

    def convertir_colonne_a_texte(self):
        for nom_feuille in ["Balance", "Balance N-1"]:
            try:
                ws = self.rf.get_sheet(self.workbook, nom_feuille)
            except Exception:
                print(f"Feuille '{nom_feuille}' introuvable, ignorée.")
                continue
            last_row = ws.Cells(ws.Rows.Count, 1).End(-4162).Row
            for row in range(1, last_row + 1):
                value = ws.Cells(row, 1).Value
                if value not in (None, ""):
                    ws.Cells(row, 1).Value = str(value)
        print("Colonne A convertie en texte")

    def effacer_donnees_et_mise_en_forme(self):
        for nom_feuille in ["Balance", "Balance N-1", "Inventaire", "Inventaire N-1", "PVMV"]:
            try:
                ws = self.rf.get_sheet(self.workbook, nom_feuille)
                ws.Cells.ClearContents()
                ws.Cells.ClearFormats()
                print(f"'{nom_feuille}' effacé")
            except Exception:
                print(f"'{nom_feuille}' introuvable, ignorée.")
        print("Données réinitialisées")

    def recreer_code_inventaire(self):
        ws_inv  = self.rf.get_sheet(self.workbook, "Inventaire N-1")
        ws_base = self.rf.get_sheet(self.workbook, "Base titres")

        last_row_inv  = ws_inv.Cells(ws_inv.Rows.Count, "C").End(-4162).Row
        last_row_base = ws_base.Cells(ws_base.Rows.Count, "C").End(-4162).Row

        base_data = []
        for row in range(2, last_row_base + 1):
            base_data.append({
                "titre":  ws_base.Cells(row, "C").Value,
                "nature": ws_base.Cells(row, "D").Value,
                "E": ws_base.Cells(row, "E").Value or "",
                "F": ws_base.Cells(row, "F").Value or "",
                "G": ws_base.Cells(row, "G").Value or "",
            })
        df_base = pd.DataFrame(base_data).set_index("titre")

        for i in range(2, last_row_inv + 1):
            titre = ws_inv.Cells(i, "C").Value
            if titre and str(titre).strip() and titre in df_base.index:
                row_base = df_base.loc[titre]
                if row_base["nature"] != "AU":
                    ws_inv.Cells(i, "B").Value = (
                        str(row_base["E"]) + str(row_base["F"]) + str(row_base["G"])
                    )
        print("Codes ISIN créés.")