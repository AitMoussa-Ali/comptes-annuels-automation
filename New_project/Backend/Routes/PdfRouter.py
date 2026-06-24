# routers/generate_pdf_router.py
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from Controllers.GeneratePdfController import GeneratePdfController, generer_bilan_pdf


class GeneratePdfRequest(BaseModel):
    """
    Body JSON attendu par POST /generatePdf/

    2 pages (bilan seul) :
    { "bilan": {...}, "nom_fond": "...", "date_cloture": "..." }

    4 pages (bilan + comptes résultats) :
    { "bilan": {...}, "compte_resultat": {...}, "nom_fond": "...", "date_cloture": "..." }

    5 pages (bilan + CR + capitaux propres) :
    {
        "bilan":            { ...BilanController... },
        "compte_resultat":  { ...CompteResultatController... },
        "capitaux_propres": { ...CapitauxPropresController... },
        "nom_fond":         "SINGULAR VENTURES I FPCI",
        "date_cloture":     "31/12/2025"
    }
    """
    bilan:            dict
    nom_fond:         str
    date_cloture:     str
    compte_resultat:  Optional[dict] = None
    capitaux_propres: Optional[dict] = None


router = APIRouter(prefix="/generatePdf", tags=["pdf"])


@router.post("/")
async def generate_pdf(request: GeneratePdfRequest):
    """
    Génère le PDF rapport complet.

    - Toujours inclus   : Bilan Actif + Bilan Passif (2 pages)
    - Si compte_resultat: + CR1 + CR2                 (4 pages)
    - Si capitaux_propres: + Capitaux Propres          (5 pages)

    Retourne le PDF en streaming (application/pdf).
    """
    if request.compte_resultat:
        pdf_bytes = await GeneratePdfController(
            bilan            = request.bilan,
            compte_resultat  = request.compte_resultat,
            nom_fond         = request.nom_fond,
            date_cloture     = request.date_cloture,
            capitaux_propres = request.capitaux_propres,
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