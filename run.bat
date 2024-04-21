@echo off
if not exist db\ (
    mkdir db
)

if not exist db\database.db (
    type nul > db\database.db
)


docker build -t tamagotchihealth .
docker run --name tamagotchihealth ^
            -v .\db:/var/db:Z ^
            -v .\frontend\dist:/home/user/frontend/dist:Z ^
            --rm ^
            -p 127.0.0.1:24242:80 ^
            -e HOST=%1 ^
            tamagotchihealth