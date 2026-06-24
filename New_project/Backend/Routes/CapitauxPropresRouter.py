# routers/capitaux_propres_router.py
from fastapi import APIRouter
from Controllers.CapitauxPropresController import CapitauxPropresController

router = APIRouter(prefix="/capitaux-propres", tags=["capitaux-propres"])


@router.post("/")
async def compute_capitaux_propres(data: dict):
    """
    Calcule la reconstitution de la ligne "Capitaux propres" (onglet III).

    Body : même structure JSON que /bilan/ et /compte-resultat/,
           retourné directement par UploadController.

    {
        "N": {
            "balance_n":    [...],
            "inventaire_n": [...],
            "pvmv":         [...]
        },
        "N_1": {                    # null si nouveau fonds (premier exercice)
            "balance_n_1":    [...],
            "inventaire_n_1": [...]
        }
    }

    Retourne :
    {
        "capitaux_propres": {
            "meta": {
                "label_col_n":          "Cumul Exercice N" | "Cumul Exercice N*",
                "label_col_n1":         "Cumul Exercice N-1" | "Cumul Exercice N-1*",
                "premier_exercice":     bool,
                "autres_elements_detail": {
                    "frais_constitution": float,   # si non nul
                    "prime_souscription": float    # si non nul
                }
            },

            // Chaque poste a la structure :
            // { "n": float, "n1": float, "variation": float }

            "capital_souscrit":               {...},
            "capital_non_appele":             {...},
            "emission_passifs_financement":   {...},
            "sous_total_apports":             {...},

            "revenus_nets_exercice":          {...},
            "cumul_revenus_nets_precedents":  {...},
            "sous_total_resultat_gestion":    {...},

            "pvmv_realisees_exercice":        {...},
            "cumul_pvmv_realisees_precedents":{...},
            "sous_total_pvmv_realisees":      {...},

            "pvmv_latentes_exercice":         {...},
            "cumul_pvmv_latentes_precedents": {...},
            "sous_total_pvmv_latentes":       {...},

            "boni_liquidation":               {...},

            "rachats":                        {...},
            "repartition_actifs":             {...},
            "distribution_resultats_nets":    {...},
            "distribution_pvmv_realisees":    {...},
            "remboursement_passifs_financement": {...},
            "sous_total_rachats_repartitions":{...},

            "label_autres_elements":          str,
            "autres_elements":                {...},

            "total_capitaux_propres":         {...}
        }
    }
    """
    return await CapitauxPropresController(data)