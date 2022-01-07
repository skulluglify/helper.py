#! /usr/bin/env bash

PASSWORD=

echo -en "Enter Password: "
read -s PASSWORD
echo

## ifconfig | grep -i inet  | grep -i 192 | head -n 1 | awk '{print $2}'

env \
MYSQL_USER=root \
MYSQL_PASSWORD=$PASSWORD \
MYSQL_HOST=127.0.0.1 \
MYSQL_DATABASE=dbtukujajan \
API_HOST=192.168.1.9 \
API_PORT=5000 \
python3 helper.py
