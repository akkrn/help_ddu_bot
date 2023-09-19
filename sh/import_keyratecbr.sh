#!/bin/bash

source ../.env
CONTAINER_NAME="help_ddu_bot-db-1"
VOLUME_PATH="/var/lib/docker/volumes/help_ddu_bot_pg_data/_data/"
sudo cp ../data/keyratecbr.csv $VOLUME_PATH
sudo docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB CREATE TABLE IF NOT EXIST keyratecbr (id SERIAL PRIMARY KEY, date DATE NOT NULL, rate REAL NOT NULL);
-c "\COPY keyratecbr FROM '/var/lib/postgresql/data//keyratecbr.csv' CSV HEADER"
