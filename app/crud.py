from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models
from typing import List, Tuple
import math

def get_organization(db: Session, org_id: int):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organizations_by_building(db: Session, building_id: int):
    return db.query(models.Organization).filter(models.Organization.building_id == building_id).all()

def get_organizations_by_activity(db: Session, activity_id: int):
    return db.query(models.Organization).join(models.Organization.activities).filter(models.Activity.id == activity_id).all()

def search_organizations_by_name(db: Session, name: str):
    return db.query(models.Organization).filter(models.Organization.name.ilike(f"%{name}%")).all()

def get_activity_with_children(db: Session, activity_id: int, max_depth: int = 3) -> List[int]:
    ids = [activity_id]

    def recurse(act_id, depth):
        if depth >= max_depth:
            return
        children = db.query(models.Activity).filter(models.Activity.parent_id == act_id).all()
        for child in children:
            ids.append(child.id)
            recurse(child.id, depth + 1)

    recurse(activity_id, 1)
    return ids

def get_organizations_by_activity_tree(db: Session, activity_id: int, max_depth: int = 3):
    activity_ids = get_activity_with_children(db, activity_id, max_depth)
    return db.query(models.Organization)\
             .join(models.Organization.activities)\
             .filter(models.Activity.id.in_(activity_ids))\
             .all()

def get_organizations_by_geo(db: Session, center: Tuple[float,float], radius_km: float):
    lat_c, lon_c = center
    km_per_deg = 111  # приближение
    lat_min = lat_c - radius_km/km_per_deg
    lat_max = lat_c + radius_km/km_per_deg
    lon_min = lon_c - radius_km/(km_per_deg*math.cos(math.radians(lat_c)))
    lon_max = lon_c + radius_km/(km_per_deg*math.cos(math.radians(lat_c)))

    return db.query(models.Organization)\
             .join(models.Organization.building)\
             .filter(and_(models.Building.latitude.between(lat_min, lat_max),
                          models.Building.longitude.between(lon_min, lon_max)))\
             .all()

def serialize_organization(db_org: models.Organization):
    return {
        "id": db_org.id,
        "name": db_org.name,
        "phone_numbers": db_org.phone_numbers.split(",") if db_org.phone_numbers else [],
        "building_id": db_org.building_id,
        "activity_ids": [a.id for a in db_org.activities],
        "building": {
            "id": db_org.building.id,
            "address": db_org.building.address,
            "latitude": db_org.building.latitude,
            "longitude": db_org.building.longitude
        } if db_org.building else None,
        "activities": [
            {
                "id": a.id,
                "name": a.name,
                "parent_id": a.parent_id,
                "children": []
            } for a in db_org.activities
        ]
    }
