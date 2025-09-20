from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from fastapi.responses import RedirectResponse
from .. import models, deps
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/buildings", tags=["Buildings"])

templates = Jinja2Templates(directory="app/templates")

# --------------------------- Buildings ---------------------------
@router.get("/")
def list_buildings(request: Request, db: Session = Depends(deps.get_db)):
    buildings = db.query(models.Building).all()
    return templates.TemplateResponse("building_list.html", {"request": request, "buildings": buildings})

@router.get("/new")
def new_building_form(request: Request):
    return templates.TemplateResponse("building_form.html", {"request": request, "building": None})

@router.post("/new")
def create_building_form(
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(deps.get_db)
):
    b = models.Building(address=address, latitude=latitude, longitude=longitude)
    db.add(b)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("building_form.html", {
            "request": {},
            "building": b,
            "error": f"Building with address '{address}' already exists."
        })
    return RedirectResponse("/buildings", status_code=303)

@router.get("/edit/{building_id}")
def edit_building_form(request: Request, building_id: int, db: Session = Depends(deps.get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        return RedirectResponse("/buildings", status_code=303)
    return templates.TemplateResponse("building_form.html", {"request": request, "building": building})

@router.post("/edit/{building_id}")
def update_building_form(
    building_id: int,
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(deps.get_db)
):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        return RedirectResponse("/buildings", status_code=303)
    building.address = address
    building.latitude = latitude
    building.longitude = longitude
    db.commit()
    return RedirectResponse("/buildings", status_code=303)

@router.get("/delete/{building_id}")
def delete_building(building_id: int, db: Session = Depends(deps.get_db)):
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if building:
        db.delete(building)
        db.commit()
    return RedirectResponse("/buildings", status_code=303)