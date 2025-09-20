from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app import models, deps, crud  # предполагаем, что функции из твоего crud.py
from app.deps import verify_api_key

router = APIRouter(prefix="/api/organizations", tags=["Organizations API"], dependencies=[Depends(verify_api_key)])

# --------------------------- Список всех организаций ---------------------------
@router.get("/", summary="Get all organizations")
def list_organizations(db: Session = Depends(deps.get_db)):
    orgs = db.query(models.Organization).all()
    return [crud.serialize_organization(o) for o in orgs]

# --------------------------- Получение по ID ---------------------------
@router.get("/{org_id}", summary="Get organization by ID")
def get_organization(org_id: int, db: Session = Depends(deps.get_db)):
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.serialize_organization(org)

# --------------------------- Поиск по имени ---------------------------
@router.get("/search/", summary="Search organizations by name")
def search_organizations(name: str = Query(..., min_length=1), db: Session = Depends(deps.get_db)):
    orgs = crud.search_organizations_by_name(db, name)
    return [crud.serialize_organization(o) for o in orgs]

# --------------------------- Фильтр по зданию ---------------------------
@router.get("/by-building/{building_id}", summary="Get organizations by building")
def organizations_by_building(building_id: int, db: Session = Depends(deps.get_db)):
    orgs = crud.get_organizations_by_building(db, building_id)
    return [crud.serialize_organization(o) for o in orgs]

# --------------------------- Фильтр по виду деятельности (с деревом) ---------------------------
@router.get("/by-activity/{activity_id}", summary="Get organizations by activity (tree)")
def organizations_by_activity(activity_id: int, db: Session = Depends(deps.get_db)):
    orgs = crud.get_organizations_by_activity_tree(db, activity_id)
    return [crud.serialize_organization(o) for o in orgs]

# --------------------------- Фильтр по координатам ---------------------------
@router.get("/by-geo/", summary="Get organizations by geo area (center + radius)")
def organizations_by_geo(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(1.0),
    db: Session = Depends(deps.get_db)
):
    orgs = crud.get_organizations_by_geo(db, (lat, lon), radius_km)
    return [crud.serialize_organization(o) for o in orgs]