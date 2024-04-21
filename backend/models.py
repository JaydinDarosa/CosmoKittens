from sqlalchemy import Column, ForeignKey, Integer, String, Float, JSON, BLOB
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    goalStepCount = Column(Integer, default=6000)


class Tamagotchi(Base):
    __tablename__ = 'tamagotchis'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    appearance = Column(JSON)
    hardware_token = Column(String)
    sprite = Column(BLOB)
    steps = Column(Integer, default=0)
    water = Column(Integer, default=100)
    food = Column(Integer, default=100)
    battery = Column(Integer, default=100)
    mood = Column(Integer, default=100)
    health = Column(Integer, default=100)




