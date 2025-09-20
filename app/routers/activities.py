from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from fastapi.responses import RedirectResponse
from .. import models, deps
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/activities", tags=["Activities"])

templates = Jinja2Templates(directory="app/templates")

# --------------------------- Activities ---------------------------
def build_activity_tree(activities):
    tree = []
    mapping = {a.id: {"id": a.id, "name": a.name, "children": []} for a in activities}
    for a in activities:
        if a.parent_id and a.parent_id in mapping:
            mapping[a.parent_id]["children"].append(mapping[a.id])
        else:
            tree.append(mapping[a.id])
    return tree

@router.get("/")
def activities_tree(request: Request, db: Session = Depends(deps.get_db)):
    activities = db.query(models.Activity).all()
    tree = build_activity_tree(activities)
    return templates.TemplateResponse("activity_tree.html", {"request": request, "activity_tree": tree})

@router.get("/new")
def new_activity_form(request: Request, db: Session = Depends(deps.get_db)):
    # Передаем все активности для выпадающего списка "Parent Activity"
    activities = db.query(models.Activity).all()
    return templates.TemplateResponse(
        "activity_form.html",
        {"request": request, "activity": None, "activities": activities}
    )

@router.post("/new")
def create_activity_form(
    name: str = Form(...),
    parent_id: int = Form(None),
    db: Session = Depends(deps.get_db)
):
    a = models.Activity(name=name, parent_id=parent_id if parent_id else None)
    db.add(a)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("activity_form.html", {
            "request": {},
            "activity": a,
            "activities": db.query(models.Activity).all(),
            "error": f"Activity with name '{name}' already exists."
        })
    return RedirectResponse("/activities/", status_code=303)

@router.get("/edit/{activity_id}")
def edit_activity_form(request: Request, activity_id: int, db: Session = Depends(deps.get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        return RedirectResponse("/activities/", status_code=303)
    # Передаем все активности для выпадающего списка "Parent Activity"
    activities = db.query(models.Activity).filter(models.Activity.id != activity_id).all()
    return templates.TemplateResponse(
        "activity_form.html",
        {"request": request, "activity": activity, "activities": activities}
    )

@router.post("/edit/{activity_id}")
def update_activity_form(
    activity_id: int,
    name: str = Form(...),
    parent_id: int = Form(None),
    db: Session = Depends(deps.get_db)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        return RedirectResponse("/activities/", status_code=303)
    activity.name = name
    activity.parent_id = parent_id if parent_id else None
    db.commit()
    return RedirectResponse("/activities/", status_code=303)

@router.get("/delete/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(deps.get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if activity:
        db.delete(activity)
        db.commit()
    return RedirectResponse("/activities/", status_code=303)