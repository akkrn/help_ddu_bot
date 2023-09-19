#!/bin/bash

source ../.env
CONTAINER_NAME="help_ddu_bot-db-1"
VOLUME_PATH="/var/lib/postgresql/data"
sudo cp ../data/keyratecbr.csv $VOLUME_PATH
sudo docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\COPY keyratecbr FROM '$VOLUME_PATH/keyratecbr.csv' CSV HEADER"
