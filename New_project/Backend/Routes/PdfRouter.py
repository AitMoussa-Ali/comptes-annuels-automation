# routers/generate_pdf_router.py
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from Controllers.GeneratePdfController import GeneratePdfController, generer_bilan_pdf


class GeneratePdfRequest(BaseModel):
    """
    Body JSON attendu par POST /generatePdf/

    Toutes les sections sont optionnelles sauf bilan, nom_fond, date_cloture.
    Pages générées dans l'ordre :
      1. Bilan Actif                (toujours)
      2. Bilan Passif               (toujours)
      3. Compte de Résultat 1       (si compte_resultat fourni)
      4. Compte de Résultat 2       (si compte_resultat fourni)
      5. Capitaux Propres           (si capitaux_propres fourni)
      6. Exposition Portefeuille    (si exposition_portefeuille fourni)
      7. Sommes Distribuables       (si sommes_distribuables fourni)

    Exemple body complet (7 pages) :
    {
        "bilan":                    { ...BilanController... },
        "compte_resultat":          { ...CompteResultatController... },
        "capitaux_propres":         { ...CapitauxPropresController... },
        "exposition_portefeuille":  { ...ExpositionPortefeuilleController... },
        "sommes_distribuables":     { ...SommesDistribuablesController... },
        "nom_fond":                 "SINGULAR VENTURES I FPCI",
        "date_cloture":             "31/12/2025"
    }
    """
    bilan:                   dict
    nom_fond:                str
    date_cloture:            str
    compte_resultat:         Optional[dict] = None
    capitaux_propres:        Optional[dict] = None
    exposition_portefeuille: Optional[dict] = None
    sommes_distribuables:    Optional[dict] = None


router = APIRouter(prefix="/generatePdf", tags=["pdf"])


@router.post("/")
async def generate_pdf(request: GeneratePdfRequest):
    """
    Génère le rapport PDF complet.
    Nombre de pages : de 2 à 7 selon les sections fournies.
    Retourne le PDF en streaming (application/pdf).
    """
    if request.compte_resultat:
        pdf_bytes = await GeneratePdfController(
            bilan                   = request.bilan,
            compte_resultat         = request.compte_resultat,
            nom_fond                = request.nom_fond,
            date_cloture            = request.date_cloture,
            capitaux_propres        = request.capitaux_propres,
            exposition_portefeuille = request.exposition_portefeuille,
            sommes_distribuables    = request.sommes_distribuables,
        )
    else:
        pdf_bytes = await generer_bilan_pdf(
            bilan        = request.bilan,
            nom_fond     = request.nom_fond,
            date_cloture = request.date_cloture,
        )

    filename = (
        f"comptes_annuels_{request.nom_fond.replace(' ', '_')}"
        f"_{request.date_cloture.replace('/', '')}.pdf"
    )

    return Response(
        content    = pdf_bytes,
        media_type = "application/pdf",
        headers    = {"Content-Disposition": f'inline; filename="{filename}"'},
    )