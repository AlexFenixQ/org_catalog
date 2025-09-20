from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import RedirectResponse
from .. import models, deps
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/organizations", tags=["Organizations"])

templates = Jinja2Templates(directory="app/templates")

# ---------------------------
# List
# ---------------------------
@router.get("/")
def list_organizations_web(request: Request, db: Session = Depends(deps.get_db)):
    orgs = db.query(models.Organization).all()
    for o in orgs:
        o.phone_numbers = o.phone_numbers.split(",") if o.phone_numbers else []
        if not hasattr(o, "activities") or o.activities is None:
            o.activities = []
    return templates.TemplateResponse("org_list.html", {"request": request, "organizations": orgs})

# ---------------------------
# Create
# ---------------------------
@router.get("/org/new")
def new_organization_form(request: Request, db: Session = Depends(deps.get_db)):
    buildings = db.query(models.Building).all()
    activities = db.query(models.Activity).all()
    return templates.TemplateResponse("org_form.html", {
        "request": request,
        "org": None,
        "buildings": buildings,
        "activities": activities
    })

@router.post("/org/new")
def create_organization_form(
    name: str = Form(...),
    phone_numbers: str = Form(...),
    building_id: int = Form(...),
    activity_ids: List[int] = Form(..., alias="activity_ids"),  # <- теперь список чисел
    db: Session = Depends(deps.get_db)
):
    activities = db.query(models.Activity).filter(models.Activity.id.in_(activity_ids)).all()
    db_org = models.Organization(
        name=name,
        phone_numbers=",".join([p.strip() for p in phone_numbers.split(",")]),
        building_id=building_id,
        activities=activities
    )
    db.add(db_org)
    db.commit()
    return RedirectResponse("/organizations", status_code=303)

# ---------------------------
# Edit
# ---------------------------
@router.get("/org/edit/{org_id}")
def edit_organization_form(request: Request, org_id: int, db: Session = Depends(deps.get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        return RedirectResponse("/organizations", status_code=303)
    
    # Преобразуем phone_numbers и activity_ids для формы
    org.phone_numbers = org.phone_numbers.split(",") if org.phone_numbers else []
    org.activity_ids = [a.id for a in org.activities] if org.activities else []

    # Загружаем все здания и активности для выпадающих списков
    buildings = db.query(models.Building).all()
    activities = db.query(models.Activity).all()

    return templates.TemplateResponse("org_form.html", {
        "request": request,
        "org": org,
        "buildings": buildings,
        "activities": activities
    })

@router.post("/org/edit/{org_id}")
def update_organization_form(
    org_id: int,
    name: str = Form(...),
    phone_numbers: str = Form(...),
    building_id: int = Form(...),
    activity_ids: List[int] = Form(..., alias="activity_ids"),  # <- теперь список чисел
    db: Session = Depends(deps.get_db)
):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        return RedirectResponse("/organizations", status_code=303)
    org.name = name
    org.phone_numbers = ",".join([p.strip() for p in phone_numbers.split(",")])
    org.building_id = building_id
    org.activities = db.query(models.Activity).filter(models.Activity.id.in_(activity_ids)).all()
    db.commit()
    return RedirectResponse("/organizations", status_code=303)

# ---------------------------
# Delete
# ---------------------------
@router.get("/org/delete/{org_id}")
def delete_organization(org_id: int, db: Session = Depends(deps.get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if org:
        db.delete(org)
        db.commit()
    return RedirectResponse("/organizations", status_code=303)