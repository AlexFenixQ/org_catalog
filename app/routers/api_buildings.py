from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app import models, deps
from app.deps import verify_api_key

router = APIRouter(prefix="/api/buildings", tags=["Buildings API"], dependencies=[Depends(verify_api_key)])

# --------------------------- Список всех зданий ---------------------------
@router.get("/", summary="Get all buildings")
def list_buildings(db: Session = Depends(deps.get_db)):
    buildings = db.query(models.Building).all()
    return [
        {"id": b.id, "address": b.address, "latitude": b.latitude, "longitude": b.longitude}
        for b in buildings
    ]

# --------------------------- Получение по ID ---------------------------
@router.get("/{building_id}", summary="Get building by ID")
def get_building(building_id: int, db: Session = Depends(deps.get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"id": building.id, "address": building.address, "latitude": building.latitude, "longitude": building.longitude}

# --------------------------- Создание ---------------------------
@router.post("/", summary="Create new building")
def create_building(address: str, latitude: float, longitude: float, db: Session = Depends(deps.get_db)):
    building = models.Building(address=address, latitude=latitude, longitude=longitude)
    db.add(building)
    try:
        db.commit()
        db.refresh(building)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Building with address '{address}' already exists.")
    return {"id": building.id, "address": building.address, "latitude": building.latitude, "longitude": building.longitude}

# --------------------------- Обновление ---------------------------
@router.put("/{building_id}", summary="Update building")
def update_building(building_id: int, address: str, latitude: float, longitude: float, db: Session = Depends(deps.get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    building.address = address
    building.latitude = latitude
    building.longitude = longitude
    db.commit()
    return {"id": building.id, "address": building.address, "latitude": building.latitude, "longitude": building.longitude}

# --------------------------- Удаление ---------------------------
@router.delete("/{building_id}", summary="Delete building")
def delete_building(building_id: int, db: Session = Depends(deps.get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(building)
    db.commit()
    return {"detail": "Building deleted"}