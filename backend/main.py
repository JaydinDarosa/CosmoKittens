from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Cookie
from sqlalchemy.orm import Session

import crud, models, schemas, utils
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authentication(auth: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if auth:
        data = utils.decode(auth)
        if data:
            return crud.get_user(db, data.get('id'))
    raise HTTPException(status_code=400, detail="Failed To authenticate")


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/login", response_model=schemas.User)
def login(logging_in_user: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=logging_in_user.username)
    if user and utils.check_password(logging_in_user.password, user.hashed_password):
        response.set_cookie("auth", utils.sign({'id': user.id}))
        return user
    raise HTTPException(status_code=400, detail="Failed To login")


@app.post('/logout')
def logout(response: Response) -> None:
    response.delete_cookie("auth")


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    user.username = user.username.strip()
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if not utils.check_username(user.username):
        raise HTTPException(status_code=400, detail="Invalid Username")
    newUser = crud.create_user(db=db, user=user)
    response.set_cookie("auth", utils.sign({"id": newUser.id}))
    return newUser


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return sorted(users, key=lambda u: u.id)


@app.get("/self", response_model=schemas.User)
def get_self(user=Depends(authentication)):
    return user


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/tamagotchis/{tamagotchi_id}", response_model=schemas.Tamagotchi)
def read_tamagotchi(tamagotchi_id: int, db: Session = Depends(get_db)):
    tamagotchi = crud.get_tamagotchi(db, tamagotchi_id=tamagotchi_id)
    if tamagotchi is None:
        raise HTTPException(status_code=404, detail="Tamagotchi not found")
    return tamagotchi


@app.post("/tamagotchis/", response_model=schemas.CreatedTamagotchi)
def create_tamagotchi(hardware_id: str, db: Session = Depends(get_db), user=Depends(authentication)):
    return crud.create_tamagotchi(db=db, owner=user, hardware_id=hardware_id)


@app.get("/self/tamagotchis", response_model=list[schemas.Tamagotchi])
def read_tamagotchis_owned(db: Session = Depends(get_db), user=Depends(authentication)):
    tamagotchis = crud.get_tamagotchis_owned(db, user=user)
    if tamagotchis is None:
        raise HTTPException(status_code=404, detail="Tamagotchis not found")
    return tamagotchis


@app.post("/sync/", response_model=schemas.Tamagotchi)
def sync_to_tamagotchi(machine_id: str, data: schemas.DataDiff,  db: Session = Depends(get_db)):
    tamagotchi = crud.sync_tamagotchi(db, machine_id, data)
    if tamagotchi is None:
        raise HTTPException(status_code=404, detail="Tamagotchi not found")
    return tamagotchi

@app.get("/sprite/{hardware_id}",
         responses={
             200: {
                 "content": {"image/png": {}}
             }
         },
         response_class=Response)
def get_sprite(hardware_id: str, db: Session = Depends(get_db)):
    tamagotchi = crud.get_tamagotchi_sprite(db, hardware_id)
    return Response(content=tamagotchi, media_type="image/png")


@app.get("/random/sprite",
         responses={
            200: {
                "content": {"image/png": {}}
            }
        },
        response_class=Response)
def get_random_sprite():
    tamagotchi = crud.get_random_tamagotchi()
    return Response(content=tamagotchi, media_type="image/png")


@app.get("/tamagotchis_sprite/{tamagotchi_id}",
         responses={
             200: {
                 "content": {"image/png": {}}
             }
         },
         response_class=Response)
def get_tamagotchi_sprite(tamagotchi_id: int, db: Session = Depends(get_db)):
    tamagotchi = crud.get_tamadachi_sprite_by_id(db, tamagotchi_id)
    return Response(content=tamagotchi, media_type="image/png")


@app.post("/update_stats/", response_model=schemas.Tamagotchi)
def update_stats(stats: schemas.updateStats, db: Session = Depends(get_db)):
    tamagotchi = crud.update_stats(db, stats)
    if tamagotchi is None:
        raise HTTPException(status_code=404, detail="Tamagotchi not found")
    return tamagotchi

