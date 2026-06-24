import pandas as pd

class Data_extraction:

    def __init__(self, fichier_vl, fichier_vl_n_1=None):
        self.fichier_vl = fichier_vl
        self.fichier_vl_n_1 = fichier_vl_n_1

    def _find_sheet(self, excel_file, target_name):
        xls = pd.ExcelFile(excel_file)

        for sheet in xls.sheet_names:
            if sheet.strip().lower() == target_name.strip().lower():
                return sheet

        raise ValueError(
            f"Sheet '{target_name}' not found. Available sheets: {xls.sheet_names}"
        )

    def extracting_data_n(self):
        balance_sheet = self._find_sheet(self.fichier_vl, "Balance")
        inventaire_sheet = self._find_sheet(self.fichier_vl, "Inventaire")
        pvmv_sheet = self._find_sheet(self.fichier_vl, "PVMV")

        balance_n = pd.read_excel(
            self.fichier_vl, balance_sheet, header=None, dtype=str
        )
        inventaire_n = pd.read_excel(
            self.fichier_vl, inventaire_sheet, header=None, dtype=str
        )
        pvmv = pd.read_excel(
            self.fichier_vl, pvmv_sheet, header=None, dtype=str
        )

        return balance_n, inventaire_n, pvmv

    def extracting_data_n_1(self):
        if self.fichier_vl_n_1 is None:
            raise ValueError("fichier_vl_n_1 requis pour les fonds anciens")

        balance_sheet = self._find_sheet(self.fichier_vl_n_1, "Balance")
        inventaire_sheet = self._find_sheet(self.fichier_vl_n_1, "Inventaire")

        balance_n_1 = pd.read_excel(
            self.fichier_vl_n_1, balance_sheet, header=None, dtype=str
        )
        inventaire_n_1 = pd.read_excel(
            self.fichier_vl_n_1, inventaire_sheet, header=None, dtype=str
        )

        return balance_n_1, inventaire_n_1