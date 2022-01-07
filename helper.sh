#! /usr/bin/env bash

PASSWORD=

echo -en "Enter Password: "
read -s PASSWORD
echo

env \
MYSQL_USER=root \
MYSQL_PASSWORD=$PASSWORD \
MYSQL_HOST=127.0.0.1 \
MYSQL_DATABASE=dbresto \
python3 helper.py
