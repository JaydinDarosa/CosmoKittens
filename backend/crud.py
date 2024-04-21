import random
import string

from sqlalchemy.orm import Session
from PIL import Image
import models, schemas
import utils


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=utils.get_hashed_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_tamagotchi(db: Session, tamagotchi_id: int):
    return db.query(models.Tamagotchi).filter(models.Tamagotchi.id == tamagotchi_id).first()


names = ["Quasar", "Asteroid", "Nebula", "Galaxy", "Star", "Meteor", "Comet", "Nova", "Cosmos", "Orbit"]


def create_tamagotchi(db: Session, owner: models.User, hardware_id: str):
    appearance = schemas.Appearance.random()
    tamagotchi_id = db.query(models.Tamagotchi).count() + 1
    name = names[hash(tamagotchi_id) % len(names)]
    token = hardware_id
    hashed_token = utils.get_hashed_password(token)
    db_tamagotchi = models.Tamagotchi(name=name, appearance=appearance, owner=owner.id, hardware_token=hashed_token)
    db.add(db_tamagotchi)
    db.commit()
    db.refresh(db_tamagotchi)

    return schemas.CreatedTamagotchi(
        id=db_tamagotchi.id,
        name=db_tamagotchi.name,
        appearance=appearance,
        owner=db_tamagotchi.owner,
        plain_token=token
    )


def get_tamagotchis_owned(db: Session, user: models.User):
    return db.query(models.Tamagotchi).filter(models.Tamagotchi.owner == user.id).all()


def sync_tamagotchi(db: Session, machine_id: str):
    hashed = utils.get_hashed_password(machine_id)
    return db.query(models.Tamagotchi).filter(models.Tamagotchi.hardware_token == hashed).first()


def sync_data(db: Session, machine_id: str, data: schemas.DataDiff):
    tamagotchi = sync_tamagotchi(db, machine_id)
    if tamagotchi is None:
        return None
    tamagotchi.steps += data.steps
    tamagotchi.water = max(0, min(100, tamagotchi.water + data.water))
    tamagotchi.food = max(0, min(100, tamagotchi.food + data.food))
    db.commit()
    db.refresh(tamagotchi)
    return tamagotchi

# def get_tamagotchis(db: Session, machine_id: str):
#     hashed = utils.get_hashed_password(machine_id)
#     tamagachi = db.query(schemas.Tamagotchi).filter(models.Tamagotchi.hardware_token == hashed).first()
#     appearance = tamagachi.appearance
#     base_texture = Image.open("assets/p_" + str(appearance.primary_color) + "_" + str(appearance.body_type) + ".png")





