#!/bin/bash

source ../.env
PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "\COPY keyratecbr TO '../data/keyratecbr.csv' CSV HEADER"
