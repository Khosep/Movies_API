#!/usr/bin/env bash

set -e

echo "Waiting for db..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.5
      echo "Sleep..."
done

echo "load_data..."
python load_data.py


