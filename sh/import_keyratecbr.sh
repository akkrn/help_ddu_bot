#!/bin/bash

source ../.env

psql -h DB_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "\COPY keyratecbr FROM '../data/keyratecbr.csv' CSV HEADER"
