# routers/compte_resultat_router.py
from fastapi import APIRouter
from Controllers.CompteResultatsController import CompteResultatController

router = APIRouter(prefix="/compte-resultat", tags=["compte-resultat"])


@router.post("/")
async def compute_compte_resultat(data: dict):
    """
    Calcule le Compte de Résultat 1 et le Compte de Résultat 2.

    Body : même structure JSON que pour /bilan/, retourné par UploadController.

    {
        "N": {
            "balance_n":    [...],
            "inventaire_n": [...],
            "pvmv":         [...]
        },
        "N_1": {                    # null si nouveau fonds
            "balance_n_1":    [...],
            "inventaire_n_1": [...]
        }
    }

    Retourne :
    {
        "compte_resultat_1": {
            "exercice_n":  { ... tous les postes CR1 ... },
            "exercice_n1": { ... }
        },
        "compte_resultat_2": {
            "exercice_n":  { ... tous les postes CR2 + resultat_net ... },
            "exercice_n1": { ... }
        },
        "controles": {
            "resultat_net_n":  float,
            "resultat_net_n1": float
        }
    }
    """
    return await CompteResultatController(data)
