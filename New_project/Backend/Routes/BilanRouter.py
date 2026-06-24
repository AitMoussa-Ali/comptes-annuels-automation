from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional
from Controllers.BilanController import BilanController

router = APIRouter(prefix="/bilan", tags=["bilan"])


@router.post("/")
async def compute_bilan(data: dict):
    return await BilanController(data)