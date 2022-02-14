#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE geo_data(id bigserial primary key, hash text, description text, shape geometry, created timestamp);
EOSQL