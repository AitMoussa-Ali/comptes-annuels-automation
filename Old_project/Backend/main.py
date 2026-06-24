from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.FondsRoutes import router as FondRouter
from Routes.UploadRoutes import router as UploadRouter
from Routes.GenerateRouter import router as GenerateRouter
app = FastAPI(title="Report Generator API")

#CORS configuration to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)

app.include_router(FondRouter, prefix="/api", tags=["reports"])
# app.include_router(UploadRouter, prefix="/api", tags=["reports"])
app.include_router(GenerateRouter, prefix="/api", tags=["reports"])