from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int


class TamagotchiBase(BaseModel):
    id: int
    name: str


class TamagotchiHardware(TamagotchiBase):
    hardware_token: str


class Appearance(BaseModel):
    primary_color: int  # 1 - 8
    secondary_color: int  # 1 - 8
    body_type: int  # 1 - 8
    hat: int

def getRandomAppearance():
    import random
    return Appearance(
        primary_color=random.randint(1, 8),
        secondary_color=random.randint(1, 8),
        body_type=random.randint(1, 8),
        hat=random.randint(0, 2)
    )


class Tamagotchi(TamagotchiBase):
    owner: int
    name: str
    appearance: str
    steps: int
    water: int
    food: int
    battery: int
    mood: int
    health: int


class DataDiff(BaseModel):
    steps: int
    battery: int

class CreatedTamagotchi(TamagotchiBase):
    owner: int
    appearance: Appearance
    plain_token: str
    id: int



