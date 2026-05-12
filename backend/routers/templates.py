from fastapi import APIRouter, HTTPException
from typing import List

from backend import schemas
from backend.services import file_io

router = APIRouter()

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

@router.get("/", response_model=List[schemas.TemplateResponse])
def list_templates():
    templates = []
    for day in DAYS:
        t = file_io.get_template(day)
        if t:
            templates.append(t)
    return templates

@router.get("/{day}", response_model=schemas.TemplateResponse)
def get_template(day: str):
    day = day.lower()
    if day not in DAYS:
        raise HTTPException(status_code=400, detail="Invalid day of week")
        
    t = file_io.get_template(day)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t

@router.put("/{day}", response_model=schemas.TemplateResponse)
def update_template(day: str, req: schemas.TemplateUpdate):
    day = day.lower()
    if day not in DAYS:
        raise HTTPException(status_code=400, detail="Invalid day of week")
        
    success = file_io.save_template(day, {"content": req.content})
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save template")
        
    return file_io.get_template(day)
