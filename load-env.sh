#!/bin/bash

while IFS='=' read -r key val; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  export "$key=$val"
  echo "$key = $val"
done < .env

echo
echo "Environment variables loaded. Restart your terminal/IDE to load them."
