from sqlalchemy.orm import Session
from app import models, database

db = database.SessionLocal()

# --- Здания ---
b1 = models.Building(address="ул. Ленина 1, офис 3", latitude=55.751, longitude=37.618)
b2 = models.Building(address="ул. Блюхера 32/1", latitude=55.755, longitude=37.62)
db.add_all([b1, b2])
db.commit()

# --- Деятельности ---
food = models.Activity(name="Еда")
db.add(food)
db.commit()

meat = models.Activity(name="Мясная продукция", parent_id=food.id)
milk = models.Activity(name="Молочная продукция", parent_id=food.id)
db.add_all([meat, milk])
db.commit()

# --- Организации ---
org1 = models.Organization(
    name="ООО Рога и Копыта",
    phone_numbers="222-222,333-333",  # храним как строку в базе
    building_id=b1.id,
    activities=[food, meat]
)

org2 = models.Organization(
    name="Молочный мир",
    phone_numbers="8-923-666-13-13",
    building_id=b2.id,
    activities=[milk]
)

db.add_all([org1, org2])
db.commit()

# --- Преобразование phone_numbers обратно в список для проверки через API ---
for org in [org1, org2]:
    org.phone_numbers = org.phone_numbers.split(",") if org.phone_numbers else []

db.close()
print("✅ Тестовые данные добавлены!")