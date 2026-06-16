
from fastapi import APIRouter,  Query
from Controllers.FondController import FondsResponse
from Controllers.FondController import GetFonds

router = APIRouter(prefix="/fonds", tags=["Fonds"])



@router.get("/", response_model=FondsResponse)
def get_fonds(
    page: int = Query(1, ge=1, description="Numéro de page (commence à 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    search: str = Query(default="", description="Filter by fund name (case-insensitive)"),
):
    return GetFonds(page=page, page_size=page_size, search=search)
