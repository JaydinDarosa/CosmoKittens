#!/bin/sh

if ! test -d ./db; then
    mkdir ./db
fi

if ! test -f ./db/database.db; then
  touch db/database.db
fi

chmod a+rwX ./db

docker build -t tamagotchihealth .
docker run --name tamagotchihealth \
            -v ./db:/var/db:Z \
            -v ./frontend/dist:/home/user/frontend/dist:Z \
            --rm \
            -p 127.0.0.1:24242:80 \
            -e HOST=$1 \
            tamagotchihealth