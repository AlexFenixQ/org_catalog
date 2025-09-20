from pydantic import BaseModel
from typing import List, Optional

class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class OrganizationBase(BaseModel):
    name: str
    phone_numbers: List[str]
    building_id: int
    activity_ids: List[int]

class Building(BuildingBase):
    id: int

    model_config = {"from_attributes": True}

class Activity(ActivityBase):
    id: int
    children: Optional[List['Activity']] = []

    model_config = {"from_attributes": True}

class Organization(OrganizationBase):
    id: int
    building: Optional[Building] = None
    activities: List[Activity] = []
    phone_numbers: List[str] = []

    model_config = {"from_attributes": True}