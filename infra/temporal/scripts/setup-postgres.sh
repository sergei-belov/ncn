#!/bin/sh
set -eu

: "${POSTGRES_SEEDS:?POSTGRES_SEEDS is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PWD:?POSTGRES_PWD is required}"

export SQL_PASSWORD="${POSTGRES_PWD}"

setup_schema() {
    database="$1"
    schema="$2"

    temporal-sql-tool \
        --plugin "${DB:-postgres12}" \
        --ep "${POSTGRES_SEEDS}" \
        -u "${POSTGRES_USER}" \
        -p "${DB_PORT:-5432}" \
        --db "${database}" \
        create
    temporal-sql-tool \
        --plugin "${DB:-postgres12}" \
        --ep "${POSTGRES_SEEDS}" \
        -u "${POSTGRES_USER}" \
        -p "${DB_PORT:-5432}" \
        --db "${database}" \
        setup-schema -v 0.0
    temporal-sql-tool \
        --plugin "${DB:-postgres12}" \
        --ep "${POSTGRES_SEEDS}" \
        -u "${POSTGRES_USER}" \
        -p "${DB_PORT:-5432}" \
        --db "${database}" \
        update-schema -d "${schema}"
}

setup_schema \
    "${DBNAME:-temporal}" \
    /etc/temporal/schema/postgresql/v12/temporal/versioned
setup_schema \
    "${VISIBILITY_DBNAME:-temporal_visibility}" \
    /etc/temporal/schema/postgresql/v12/visibility/versioned
