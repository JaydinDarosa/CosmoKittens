import random
import string
from io import BytesIO

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
    appearance = schemas.getRandomAppearance()
    appearanceStringJson = appearance.json()
    tamagotchi_id = db.query(models.Tamagotchi).count() + 1
    name = names[hash(tamagotchi_id) % len(names)]
    token = hardware_id
    hashed_token = token
    db_tamagotchi = models.Tamagotchi(name=name, appearance=appearanceStringJson, owner=owner.id, hardware_token=hashed_token)
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


def sync_tamagotchi(db: Session, machine_id: str, data: schemas.DataDiff):
    tamagotchi = db.query(models.Tamagotchi).filter(models.Tamagotchi.hardware_token == machine_id).first()
    if tamagotchi is None:
        return None
    tamagotchi.steps += data.steps
    foodScore = (tamagotchi.food / 100) * 4 # Scale food score of 0 - 4
    waterScore = (tamagotchi.water / 100) * 4 # Scale water score of 0 - 4
    user = db.query(models.User).filter(models.User.id == tamagotchi.owner).first()
    stepScore = (tamagotchi.steps / user.goalStepCount) * 4 # Scale step score of 0 - 4
    finalScore = (foodScore + waterScore + stepScore) / 3
    happiness = round(finalScore)
    tamagotchi.battery = data.battery
    tamagotchi.mood = happiness


    db.commit()
    db.refresh(tamagotchi)
    return tamagotchi


def get_tamagotchi_sprite(db: Session, machine_id: str):
    tamagachi = db.query(models.Tamagotchi).filter(models.Tamagotchi.hardware_token == machine_id).first()
    if tamagachi is None:
        return None
    appearanceStringJson = tamagachi.appearance
    appearance = schemas.Appearance.parse_raw(appearanceStringJson)
    base_texture = Image.open("assets/pp_" + str(appearance.primary_color) + "_" + str(appearance.body_type) + ".png").convert("RGBA")
    secondary_texture = Image.open("assets/sp_" + str(appearance.secondary_color) + "_" + str(appearance.body_type) + ".png").convert("RGBA")
    tamagotchi = Image.new("RGBA", base_texture.size)
    tamagotchi.paste(base_texture, [0, 0], base_texture)
    tamagotchi.paste(secondary_texture, [0, 0], secondary_texture)
    membuf = BytesIO()
    tamagotchi.save(membuf, format="PNG")
    return membuf.getvalue()









