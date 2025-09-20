from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import activities
from app.routers import buildings
from app.routers import organizations
from app.routers import api_activities
from app.routers import api_buildings
from app.routers import api_organizations

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(activities.router)
app.include_router(buildings.router)
app.include_router(organizations.router)
app.include_router(api_activities.router)
app.include_router(api_buildings.router)
app.include_router(api_organizations.router)