# routers/sommes_distribuables_router.py
from fastapi import APIRouter
from Controllers.SommesDistribuablesController import SommesDistribuablesController

router = APIRouter(prefix="/sommes-distribuables", tags=["sommes-distribuables"])


@router.post("/")
async def compute_sommes_distribuables(data: dict):
    """
    Calcule la détermination et ventilation des sommes distribuables
    (onglet XIII du template Aplitec).

    Body : même structure JSON que /bilan/ — retourné directement par UploadController.

    {
        "N": {
            "balance_n":    [...],
            "inventaire_n": [...],
            "pvmv":         [...]
        },
        "N_1": {          # null si nouveau fonds (premier exercice)
            "balance_n_1":    [...],
            "inventaire_n_1": [...]
        }
    }

    Retourne :
    {
        "sommes_distribuables": {
            "meta": {
                "label_exercice_n":  "Exercice N" | "Exercice N*",
                "label_exercice_n1": "Exercice N-1" | "Exercice N-1*",
                "premier_exercice":  bool,
                "note_generale":     str
            },

            "revenus_nets": {
                "revenus_nets":                 { "n": float, "n1": float },
                "acomptes_sur_revenus_nets":    { "n": float, "n1": float },
                "revenus_exercice_a_affecter":  { "n": float, "n1": float },
                "report_a_nouveau":             { "n": float, "n1": float },
                "sommes_distribuables_revenus": { "n": float, "n1": float },
                "affectation": {
                    "distribution":         { "n": float, "n1": float },
                    "report_a_nouveau_exo": { "n": float, "n1": float },
                    "capitalisation":       { "n": float, "n1": float },
                    "total":                { "n": float, "n1": float }
                },
                "acomptes_info":  { "montant_unitaire": {...}, "credits_impots_totaux": {...}, "credits_impots_unitaires": {...} },
                "parts_info":     { "nombre_parts": {...}, "distribution_unitaire": {...}, "credit_impot_distribution": {...} }
            },

            "pvmv_realisees": {
                "pvmv_realisees_nettes":             { "n": float, "n1": float },
                "acomptes_sur_pvmv_realisees":       { "n": float, "n1": float },
                "pvmv_realisees_a_affecter":         { "n": float, "n1": float },
                "pvmv_anterieures_non_distribuees":  { "n": float, "n1": float },
                "sommes_distribuables_pvmv":         { "n": float, "n1": float },
                "affectation": {
                    "distribution":          { "n": float, "n1": float },
                    "report_a_nouveau_pvmv": { "n": float, "n1": float },
                    "capitalisation":        { "n": float, "n1": float },
                    "total":                 { "n": float, "n1": float }
                },
                "acomptes_info": { "acomptes_unitaires": {...} },
                "parts_info":    { "nombre_parts": {...}, "distribution_unitaire": {...} }
            }
        }
    }
    """
    return await SommesDistribuablesController(data)