#!/usr/bin/env bash

set -e

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f movies_database.ddl
