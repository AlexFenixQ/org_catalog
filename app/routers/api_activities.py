from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app import models, deps, crud
from app.deps import verify_api_key

router = APIRouter(prefix="/api/activities", tags=["Activities API"], dependencies=[Depends(verify_api_key)])

# --------------------------- Построение дерева активностей ---------------------------
def build_activity_tree(activities):
    tree = []
    mapping = {a.id: {"id": a.id, "name": a.name, "parent_id": a.parent_id, "children": []} for a in activities}
    for a in activities:
        if a.parent_id and a.parent_id in mapping:
            mapping[a.parent_id]["children"].append(mapping[a.id])
        else:
            tree.append(mapping[a.id])
    return tree

# --------------------------- Список всех активностей (дерево) ---------------------------
@router.get("/", summary="Get all activities in tree structure")
def get_activities(db: Session = Depends(deps.get_db)):
    activities = db.query(models.Activity).all()
    return build_activity_tree(activities)

# --------------------------- Получение по ID ---------------------------
@router.get("/{activity_id}", summary="Get activity by ID")
def get_activity(activity_id: int, db: Session = Depends(deps.get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return {"id": activity.id, "name": activity.name, "parent_id": activity.parent_id}

# --------------------------- Создание ---------------------------
@router.post("/", summary="Create new activity")
def create_activity(name: str, parent_id: int = None, db: Session = Depends(deps.get_db)):
    a = models.Activity(name=name, parent_id=parent_id)
    db.add(a)
    try:
        db.commit()
        db.refresh(a)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Activity with name '{name}' already exists")
    return {"id": a.id, "name": a.name, "parent_id": a.parent_id}

# --------------------------- Обновление ---------------------------
@router.put("/{activity_id}", summary="Update activity")
def update_activity(activity_id: int, name: str, parent_id: int = None, db: Session = Depends(deps.get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity.name = name
    activity.parent_id = parent_id
    db.commit()
    return {"id": activity.id, "name": activity.name, "parent_id": activity.parent_id}

# --------------------------- Удаление ---------------------------
@router.delete("/{activity_id}", summary="Delete activity")
def delete_activity(activity_id: int, db: Session = Depends(deps.get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return {"detail": "Activity deleted"}