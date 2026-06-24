import pandas as pd
from Parsers.Balance_parser import parse_balance
from Parsers.Inventaire_parser import parser_inventaire
from Parsers.Pvmv_parser import parser_pvmv
class Data_extraction:

    def __init__(self, fichier_vl, fichier_vl_n_1=None):
        self.fichier_vl = fichier_vl
        self.fichier_vl_n_1 = fichier_vl_n_1

    async def extracting_data_n(self):
        vl_n = pd.ExcelFile(self.fichier_vl)
        print("parsiiing")
        balance_n, inventaire_n, pvmv = (
            await parse_balance(vl_n),
            await parser_inventaire(vl_n),
            await parser_pvmv(vl_n),
        )
        return {
            "balance_n": balance_n,
            "inventaire_n": inventaire_n,
            "pvmv": pvmv,
        }

    async def extracting_data_n_1(self):
        if self.fichier_vl_n_1 is None:
            raise ValueError("fichier_vl_n_1 requis pour les fonds anciens")
        
        vl_n_1 = pd.ExcelFile(self.fichier_vl_n_1)
        balance_n_1, inventaire_n_1 = (await parse_balance(vl_n_1), await parser_inventaire(vl_n_1))
        
        result_n_1 = {
                "balance_n_1": balance_n_1,
                "inventaire_n_1": inventaire_n_1,
            }
        
        return result_n_1