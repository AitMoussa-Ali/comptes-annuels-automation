# routers/exposition_portefeuille_router.py
from fastapi import APIRouter
from Controllers.ExpositionPortefeuilleController import ExpositionPortefeuilleController

router = APIRouter(prefix="/exposition-portefeuille", tags=["exposition-portefeuille"])


@router.post("/")
async def compute_exposition_portefeuille(data: dict):
    """
    Calcule la ventilation de l'exposition sur les portefeuilles de
    capital-investissement (onglet VIII du template Aplitec).

    Body : même structure JSON que /bilan/ — retourné directement par UploadController.

    {
        "N": {
            "balance_n":    [...],
            "inventaire_n": [...],   ← source principale (valeurs d'estimation)
            "pvmv":         [...]
        },
        "N_1": {                     # null si nouveau fonds
            "balance_n_1":    [...],
            "inventaire_n_1": [...]
        }
    }

    Retourne :
    {
        "exposition_portefeuille": {
            "exercice_n": {
                "actions": {
                    "cotees":     { "capital_investissement": float, "autres_actifs": float, "total": float },
                    "non_cotees": { ... }
                },
                "obligations_convertibles": { "cotees": {...}, "non_cotees": {...} },
                "autres_obligations":       { "cotees": {...}, "non_cotees": {...} },
                "titres_creances":          { "capital_investissement": float, "autres_actifs": float, "total": float },
                "parts_opc":               { ... },
                "prets":                   { ... },
                "autres_actifs_eligibles": { ... },
                "total":                   { "capital_investissement": float, "autres_actifs": float, "total": float }
            },
            "exercice_n1": { ... }   // absent si N_1 est null
        }
    }
    """
    return await ExpositionPortefeuilleController(data)