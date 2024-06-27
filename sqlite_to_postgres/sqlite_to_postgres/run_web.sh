#!/usr/bin/env bash

set -e

echo "Waiting for db..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.5
      echo "Sleeping..."
done

echo "Loading data..."
python load_data.py

echo "Loading finished"


