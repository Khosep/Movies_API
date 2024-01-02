#!/usr/bin/env bash

set -e

#sudo -u postgres -H -- psql -d database_name -c "CREATE DATABASE $POSTGRES_DB;"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f movies_database.ddl

#psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;"
#psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f movies_database.ddl



