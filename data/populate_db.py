from sqlalchemy.orm import Session
from app import models, database

db: Session = database.SessionLocal()

# --- Функции для безопасного создания ---
def get_or_create_building(address, latitude, longitude):
    building = db.query(models.Building).filter(models.Building.address == address).first()
    if building:
        return building
    building = models.Building(address=address, latitude=latitude, longitude=longitude)
    db.add(building)
    db.commit()
    db.refresh(building)
    return building

def get_or_create_activity(name, parent=None):
    activity = db.query(models.Activity).filter(models.Activity.name == name).first()
    if activity:
        return activity
    parent_id = parent.id if parent else None
    activity = models.Activity(name=name, parent_id=parent_id)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

def get_or_create_organization(name, phone_numbers, building, activities):
    org = db.query(models.Organization).filter(models.Organization.name == name).first()
    if org:
        return org
    org = models.Organization(
        name=name,
        phone_numbers=",".join(phone_numbers),
        building_id=building.id,
        activities=activities
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

# --- Создание зданий ---
b1 = get_or_create_building("ул. Ленина 1, офис 3", 55.751, 37.618)
b2 = get_or_create_building("ул. Блюхера 32/1", 55.755, 37.62)

# --- Создание деятельности ---
food = get_or_create_activity("Еда")
meat = get_or_create_activity("Мясная продукция", parent=food)
milk = get_or_create_activity("Молочная продукция", parent=food)

# --- Создание организаций ---
org1 = get_or_create_organization(
    "ООО Рога и Копыта",
    ["222-222", "333-333"],
    b1,
    [food, meat]
)

org2 = get_or_create_organization(
    "Молочный мир",
    ["8-923-666-13-13"],
    b2,
    [milk]
)

# --- Преобразование phone_numbers обратно в список для проверки через API ---
for org in [org1, org2]:
    org.phone_numbers = org.phone_numbers.split(",") if org.phone_numbers else []

db.close()
print("✅ Тестовые данные добавлены/проверены!")