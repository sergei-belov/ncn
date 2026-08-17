#!/bin/bash
POSTGRES_DBS="
ncn
stage-ncn
"

set -e
for DB in $POSTGRES_DBS
do
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE DATABASE \"$DB\";" -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB\" TO \"$POSTGRES_USER\";"
done
