#!/bin/bash

TOKEN=$(grep SECRET_TOKEN medifacil_backend/.env | cut -d '=' -f2)

curl --location 'http://127.0.0.1:8000/scraper' \
--header 'Content-Type: application/json' \
--data '{
    "spiders": [
        "CrawlFybeca",
        "CrawlMedicity",
        "CrawlCruzAzul"
    ],
    "token": "'"$TOKEN"'"
}'
