import pandas as pd
from io import BytesIO

class Data_extraction:

    def __init__(self, fichier_vl, fichier_vl_n_1=None):
        self.fichier_vl = fichier_vl        # bytes ou path
        self.fichier_vl_n_1 = fichier_vl_n_1

    def extracting_data_n(self): 
        balance_n    = pd.read_excel(self.fichier_vl, "Balance ",   header=None, dtype=str)
        inventaire_n = pd.read_excel(self.fichier_vl, "Inventaire", header=None, dtype=str)
        pvmv         = pd.read_excel(self.fichier_vl, "PVMV",       header=None, dtype=str)
        return balance_n, inventaire_n, pvmv

    def extracting_data_n_1(self):
        if self.fichier_vl_n_1 is None:
            raise ValueError("fichier_vl_n_1 requis pour les fonds anciens (ancienneté A)")
        balance_n_1    = pd.read_excel(self.fichier_vl_n_1, "Balance ",   header=None, dtype=str)
        inventaire_n_1 = pd.read_excel(self.fichier_vl_n_1, "Inventaire", header=None, dtype=str)
        return balance_n_1, inventaire_n_1