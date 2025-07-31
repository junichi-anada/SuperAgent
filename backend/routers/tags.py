from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/api/v1/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)

@router.get("/personalities", response_model=List[schemas.Personality])
def get_personalities(db: Session = Depends(get_db)):
    return crud.get_personalities(db)

@router.get("/roles", response_model=List[schemas.Role])
def get_roles(db: Session = Depends(get_db)):
    return crud.get_roles(db)

@router.get("/tones", response_model=List[schemas.Tone])
def get_tones(db: Session = Depends(get_db)):
    return crud.get_tones(db)