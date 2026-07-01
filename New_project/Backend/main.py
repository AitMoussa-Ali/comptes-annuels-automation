from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.UploadRouter import router as UploadRouter
from Routes.BilanRouter import router as BilanRouter
from Routes.PdfRouter import router as PdfRouter
from Routes.CompteResultatsRouter import router as CompteResultatRouter
from Routes.CapitauxPropresRouter import router as CapitauxPropresRouter
from Routes.SommesDistribuablesRouter import router as SommesDistribuablesRouter
from Routes.ExpositionPortefeuilleRouter import router as ExpositionPortefeuilleRouter
from Routes.CompanyRouter import router as CompanyRouter
from database import Base, engine
from Routes.FundRouter import router as FundRouter
from Models.CompanyModel import Company   # noqa: F401
from Models.FundModel import Fund      

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Report Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)

app.include_router(UploadRouter, prefix="/api", tags=["reports"])
app.include_router(BilanRouter, prefix="/api", tags=["bilan"])
app.include_router(PdfRouter, prefix="/api", tags=["generation"])
app.include_router(CompteResultatRouter, prefix="/api", tags=["compte resultat"])
app.include_router(CapitauxPropresRouter, prefix="/api", tags=["Capitaux propres"])
app.include_router(ExpositionPortefeuilleRouter, prefix="/api", tags=["Expositions portefeuille"])
app.include_router(SommesDistribuablesRouter, prefix="/api", tags=["Sommes Distribuables"])
app.include_router(CompanyRouter, prefix="/api", tags=["Companies"])
app.include_router(FundRouter, prefix="/api", tags=["Funds"])
