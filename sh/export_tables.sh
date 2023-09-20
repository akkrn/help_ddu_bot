#!/bin/bash

source ../.env

TABLES=("users" "penalties" "defects" "questions")
for TABLE in "${TABLES[@]}"
do
  sudo docker exec -it help_ddu_bot-db-1 psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\COPY $TABLE TO STDOUT WITH CSV HEADER" > /var/www/help_ddu_bot/$TABLE.csv 
done
